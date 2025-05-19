from flask import Flask, request, Response
import pika
import xml.etree.ElementTree as ET
import json
import uuid
import threading

app = Flask(__name__)

# Conexión con RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

response_data = {}
lock = threading.Lock()

@app.route("/soap", methods=["POST"])
def soap_handler():
    try:
        # Parsear XML entrante
        tree = ET.fromstring(request.data)
        ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
              'web': 'http://web.service/'}
        
        engine = tree.find('.//web:engine', ns).text
        operation = tree.find('.//web:operation', ns).text
        payload_raw = tree.find('.//web:payload', ns).text
        payload = json.loads(payload_raw)

        correlation_id = str(uuid.uuid4())
        queue_name = f"reply_queue_{correlation_id}"
        result = channel.queue_declare(queue=queue_name, exclusive=True)
        callback_queue = result.method.queue

        def on_response(ch, method, props, body):
            if props.correlation_id == correlation_id:
                with lock:
                    response_data[correlation_id] = body.decode()

        channel.basic_consume(queue=callback_queue,
                              on_message_callback=on_response,
                              auto_ack=True)

        message = {
            'engine': engine,
            'operation': operation,
            'payload': payload
        }

        channel.basic_publish(
            exchange='',
            routing_key='db_rpc_queue',
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=correlation_id,
            ),
            body=json.dumps(message)
        )

        # Esperar respuesta
        while correlation_id not in response_data:
            connection.process_data_events()

        # Construir respuesta SOAP
        result_json = response_data[correlation_id]
        soap_response = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <response>
                    {result_json}
                </response>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        return Response(soap_response, mimetype='text/xml')

    except Exception as e:
        return Response(f"<error>{str(e)}</error>", status=500, mimetype='text/xml')

if __name__ == "__main__":
    print("SOAP Gateway activo en http://localhost:8000/soap")
    app.run(port=8000)
