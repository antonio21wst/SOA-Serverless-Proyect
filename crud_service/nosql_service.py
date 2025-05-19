import pika
import json
from pymongo import MongoClient

# Conexión MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Conexión RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="sql_queue")

def handle_nosql_operation(operation, payload):
    try:
        # Usar base de datos dinámica
        dbname = payload.get("dbname", "test")
        db = client[dbname]
        collection = db[payload["collection"]]

        if operation == "CREATE":
            result = collection.insert_one(payload["document"])
            return {"inserted_id": str(result.inserted_id)}
        elif operation == "READ":
            query = payload.get("filter", {})
            docs = list(collection.find(query, {"_id": 0}))
            return {"result": docs}
        elif operation == "UPDATE":
            result = collection.update_one(payload["filter"], {"$set": payload["update"]})
            return {"modified_count": result.modified_count}
        elif operation == "DELETE":
            result = collection.delete_one(payload["filter"])
            return {"deleted_count": result.deleted_count}
        elif operation == "AGGREGATE":
            pipeline = payload["pipeline"]
            result = list(collection.aggregate(pipeline))
            return {"result": result}
        else:
            return {"error": "Operación NoSQL no reconocida"}

    except Exception as e:
        return {"error": str(e)}

def on_request(ch, method, props, body):
    data = json.loads(body)
    if data["engine"] != "nosql":
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    operation = data["operation"]
    payload = data["payload"]
    response = handle_nosql_operation(operation, payload)

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

print("[NoSQL SERVICE] Esperando mensajes...")
channel.basic_consume(queue="sql_queue", on_message_callback=on_request)
channel.start_consuming()
