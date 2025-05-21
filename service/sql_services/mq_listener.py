# mq_listener.py
import pika
import json
from sql_handler import handle_sql_operation

def on_request(ch, method, properties, body):
    try:
        message = json.loads(body)
        if message.get("engine") != "sql":
            return

        operation = message.get("operation")
        payload = message.get("payload", {})

        response = handle_sql_operation(operation, payload)
    except Exception as e:
        response = {"error": f"Excepción en el SQL service: {str(e)}"}

    if properties.reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )

def start_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue="sql_queue")
    channel.basic_consume(queue="sql_queue", on_message_callback=on_request, auto_ack=True)

    print(" [*] Esperando mensajes de SQL. Para salir presiona CTRL+C")
    channel.start_consuming()
