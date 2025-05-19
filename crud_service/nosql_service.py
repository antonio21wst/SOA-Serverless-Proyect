'''
import pika
import json
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mi_basedatos"]

def handle_message(ch, method, properties, body):
    request = json.loads(body)
    op = request['operation']
    p = request['payload']
    response = ""

    try:
        collection = db[p['collection']]

        if op == 'nosql_insert':
            result = collection.insert_one(p['document'])
            response = str(result.inserted_id)
        elif op == 'nosql_read':
            result = list(collection.find(p['filters'], {'_id': False}))
            response = json.dumps(result)
        elif op == 'nosql_update':
            collection.update_many(p['filters'], {'$set': p['updates']})
            response = "OK"
        elif op == 'nosql_delete':
            collection.delete_many(p['filters'])
            response = "OK"
        elif op == 'nosql_aggregate':
            pipeline = p['pipeline']
            result = list(collection.aggregate(pipeline))
            response = json.dumps(result)
        else:
            response = "Operación no válida"
    except Exception as e:
        response = f"Error: {str(e)}"

    ch.basic_publish(
        exchange='',
        routing_key=properties.reply_to,
        properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        body=response
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Setup RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='nosql_queue')
channel.basic_consume(queue='nosql_queue', on_message_callback=handle_message)
print("[MongoDB] Esperando mensajes...")
channel.start_consuming()
'''
import pika
import json
from pymongo import MongoClient

# Configuración MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["test_nosql"]

# Conexión RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="db_rpc_queue")

def handle_nosql_operation(operation, payload):
    try:
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
channel.basic_consume(queue="db_rpc_queue", on_message_callback=on_request)
channel.start_consuming()
