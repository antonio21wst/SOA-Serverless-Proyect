
from flask import Flask, request, render_template, jsonify
import pika
import uuid
import json

app = Flask(__name__)

def call_rpc(payload):
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
        routing_key='sql_queue',
        properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=corr_id),
        body=json.dumps(payload)
    )

    while response is None:
        connection.process_data_events()

    connection.close()
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        engine = request.form['engine']
        operation = request.form['operation']
        dbname = request.form.get('dbname', 'postgres')
        payload_raw = request.form['payload']

        try:
            payload_json = json.loads(payload_raw)
            # Agregamos dbname al payload
            payload_json['dbname'] = dbname

            rpc_payload = {
                "engine": engine,
                "operation": operation,
                "payload": payload_json
            }
            result = call_rpc(rpc_payload)
        except Exception as e:
            result = {"error": str(e)}

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
