from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from flask_session import Session
from requests_oauthlib import OAuth2Session
from soap_utils import parse_soap_request, build_soap_response
import os
import pika
import uuid
import json
import requests
import time

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Permitir HTTP para pruebas

# === Configuración de Flask ===
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# === Cargar credenciales desde JSON ===
with open('soap_client_test/client_secret_1018285043352-4gs36duirt321bio4nmcssb18ce8d3sd.apps.googleusercontent.com.json') as f:
    google_creds = json.load(f)['web']
GOOGLE_CLIENT_ID = google_creds['client_id']
GOOGLE_CLIENT_SECRET = google_creds['client_secret']
REDIRECT_URI = google_creds['redirect_uris'][0]
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
SCOPES = ['openid', 'email', 'profile']

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# === RabbitMQ RPC ===
def call_rpc(payload, queue):
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue
    corr_id = str(uuid.uuid4())
    response = None

    def on_response(ch, method, props, body):
        nonlocal response
        if props.correlation_id == corr_id:
            response = json.loads(body)

    channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

    channel.basic_publish(
        exchange='',
        routing_key=queue,
        properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=corr_id),
        body=json.dumps(payload)
    )

    timeout_seconds = 10
    waited = 0
    while response is None and waited < timeout_seconds:
        connection.process_data_events(time_limit=1)
        waited += 1

    connection.close()
    if response is None:
        return {"error": "Tiempo de espera agotado para la respuesta RPC"}
    return response

# === Rutas ===
@app.route('/soap', methods=['POST'])
def soap_endpoint():
    try:
        xml_data = request.data
        parsed = parse_soap_request(xml_data)

        engine = parsed['engine']
        operation = parsed['operation']
        dbname = parsed['dbname']
        payload = json.loads(parsed['payload'])  # payload está como string JSON

        payload['dbname'] = dbname
        rpc_payload = {
            "engine": engine,
            "operation": operation,
            "payload": payload
        }

        if engine == "sql":
            queue = "sql_queue"
        elif engine == "nosql":
            queue = "nosql_queue"
        else:
            return build_soap_response({"error": "Engine inválido"}), 400, {'Content-Type': 'text/xml'}

        result = call_rpc(rpc_payload, queue)

        xml_response = build_soap_response(result)
        return xml_response, 200, {'Content-Type': 'text/xml'}

    except Exception as e:
        error_response = build_soap_response({"error": str(e)})
        return error_response, 500, {'Content-Type': 'text/xml'}

@app.route('/login')
def login():
    mensaje = request.args.get("mensaje")
    if not mensaje:
        google = OAuth2Session(GOOGLE_CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
        authorization_url, state = google.authorization_url(
            google_creds['auth_uri'],
            access_type='offline',
            prompt='consent'
        )
        session['oauth_state'] = state
        return redirect(authorization_url)

    return render_template("login.html", mensaje=mensaje)

@app.route('/callback/google')
def callback():
    if 'oauth_state' not in session:
        return redirect(url_for('login'))

    google = OAuth2Session(GOOGLE_CLIENT_ID, state=session['oauth_state'], redirect_uri=REDIRECT_URI)
    token = google.fetch_token(
        google_creds['token_uri'],
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=request.url
    )
    userinfo = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    session['user'] = {
        'name': userinfo.get('name'),
        'email': userinfo.get('email'),
        'picture': userinfo.get('picture')
    }
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    user = session.get("user")

    if not user:
        return redirect(url_for('login', mensaje="Bienvenido, inicie sesión para acceder al servicio"))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            engine = data['engine']
            dbname = data.get('dbname', 'postgres')
            operation = data['operation']
            payload = data['payload']
            payload['dbname'] = dbname
            rpc_payload = {"engine": engine, "operation": operation, "payload": payload}

            if engine == "sql":
                queue = "sql_queue"
            elif engine == "nosql":
                queue = "nosql_queue"
            else:
                return jsonify({"error": "Engine inválido. Debe ser 'sql' o 'nosql'"}), 400

            result = call_rpc(rpc_payload, queue)
            return jsonify(result)

        try:
            engine = request.form['engine']
            dbname = request.form.get('dbname', 'postgres')
            operation = request.form['operation']
            payload_raw = request.form['payload']
            payload_json = json.loads(payload_raw)
            payload_json['dbname'] = dbname
            rpc_payload = {"engine": engine, "operation": operation, "payload": payload_json}

            if engine == "sql":
                queue = "sql_queue"
            elif engine == "nosql":
                queue = "nosql_queue"
            else:
                return render_template('index.html', result={"error": "Engine inválido. Debe ser 'sql' o 'nosql'"}, user=user)

            result = call_rpc(rpc_payload, queue)

        except Exception as e:
            result = {"error": str(e)}

        return render_template('index.html', result=result, user=user)

    return render_template('index.html', result=None, user=user)

if __name__ == '__main__':
    app.run(debug=True)
