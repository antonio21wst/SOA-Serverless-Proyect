from flask import Flask, request, jsonify
import psycopg2
import pika
import json

app = Flask(__name__)

def handle_sql_operation(operation, payload):
    dbname = payload.get("dbname", "postgres") 
    query = payload.get("query", "")
    if not query:
        return {"error": "No se proporcionó ninguna consulta SQL"}

    try:
        # Si la consulta es CREATE DATABASE, conectarse a 'postgres' y activar autocommit
        if "create database" in query.lower():
            conn = psycopg2.connect(
                dbname="postgres", user="postgres", password="1234", host="localhost", port="5432"
            )
            conn.autocommit = True  #  Necesario para CREATE DATABASE
            cursor = conn.cursor()
            cursor.execute(query)
            return {"status": "Base de datos creada correctamente"}
        else:
            # Conectarse a la base de datos especificada
            conn = psycopg2.connect(
                dbname=dbname, user="postgres", password="1234", host="localhost", port="5432"
            )
            cursor = conn.cursor()

            if operation in ["CREATE", "UPDATE", "DELETE"]:
                cursor.execute(query)
                conn.commit()
                return {"status": "ok"}

            elif operation in ["READ", "JOIN"]:
                cursor.execute(query)
                result = cursor.fetchall()
                return {"result": result}

            elif operation == "AGGREGATE":
                cursor.execute(query)
                result = cursor.fetchone()
                return {"result": result}

            else:
                return {"error": "Operación SQL no reconocida"}

    except Exception as e:
        return {"error": str(e)}

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
'''
def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        if message.get("engine") != "sql":
            return  # Ignorar si no es para este servicio

        operation = message.get("operation")
        payload = message.get("payload", {})

        response = handle_sql_operation(operation, payload)
    except Exception as e:
        response = {"error": f"Excepción en el SQL service: {str(e)}"}

    # Enviar la respuesta aunque haya error
    
    if properties.reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )
'''
def on_request(ch, method, properties, body):
    try:
        message = json.loads(body)
        if message.get("engine") != "sql":
            return  # Ignorar si no es para este servicio

        operation = message.get("operation")
        payload = message.get("payload", {})

        response = handle_sql_operation(operation, payload)
    except Exception as e:
        response = {"error": f"Excepción en el SQL service: {str(e)}"}

    # Enviar la respuesta aunque haya error
    
    if properties.reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )

channel = pika.BlockingConnection(pika.ConnectionParameters("localhost")).channel()
channel.queue_declare(queue="sql_queue")
channel.basic_consume(queue='sql_queue', on_message_callback=on_request, auto_ack=True)


print(" [*] Esperando mensajes de SQL. Para salir presiona CTRL+C")
channel.start_consuming()
