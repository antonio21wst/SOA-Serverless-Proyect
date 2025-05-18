# messaging_service/producer.py
import pika
import json

def send_message(queue, message_dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    message = json.dumps(message_dict)
    channel.basic_publish(exchange='', routing_key=queue, body=message)
    print(f"[x] Mensaje enviado a {queue}: {message}")
    connection.close()

# INSERT PostgreSQL
send_message("sql_queue", {
    "operation": "insert_user",
    "payload": {"name": "Juan", "email": "juan@example.com"}
})

# GET PostgreSQL
send_message("sql_queue", {
    "operation": "get_users",
    "payload": {}
})

# INSERT MongoDB
send_message("nosql_queue", {
    "operation": "insert_user",
    "payload": {"name": "Ana", "email": "ana@example.com"}
})

# GET MongoDB
send_message("nosql_queue", {
    "operation": "get_users",
    "payload": {}
})
