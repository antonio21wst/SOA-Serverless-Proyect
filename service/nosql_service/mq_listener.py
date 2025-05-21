# mq_listener.py
import pika
import json
from nosql_handler import handle_nosql_operation

def on_request(ch, method, props, body):
    try:
        data = json.loads(body)

        if data.get("engine") != "nosql":
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        operation = data["operation"]
        payload = data["payload"]
        response = handle_nosql_operation(operation, payload)

    except Exception as e:
        response = {"error": f"Error en el servicio NoSQL: {str(e)}"}

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="nosql_queue")
    channel.basic_consume(queue="nosql_queue", on_message_callback=on_request, auto_ack=False)

    print("[NoSQL SERVICE] Esperando mensajes...")
    channel.start_consuming()
