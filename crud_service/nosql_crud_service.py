# crud_service/nosql_crud_service.py
import pika
import json
from pymongo import MongoClient

def process_nosql_crud(message):
    data = json.loads(message)
    operation = data.get("operation")
    payload = data.get("payload")

    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_nosql"]
    collection = db["users"]

    if operation == "insert_user":
        collection.insert_one(payload)

    elif operation == "get_users":
        users = list(collection.find({}, {"_id": 0}))
        print("Usuarios MongoDB:", users)

    client.close()


# RabbitMQ listener
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='nosql_queue')

def callback(ch, method, properties, body):
    print("[NoSQL] Mensaje recibido:", body.decode())
    process_nosql_crud(body.decode())

channel.basic_consume(queue='nosql_queue', on_message_callback=callback, auto_ack=True)

print("[NoSQL] Esperando mensajes NoSQL...")
channel.start_consuming()
