''' 
import pika
import json
import psycopg2

conn = psycopg2.connect(
    dbname='test_db',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)
cursor = conn.cursor()

def handle_message(ch, method, properties, body):
    request = json.loads(body)
    op = request['operation']
    payload = request['payload']
    response = ""

    try:
        if op == 'create_user':
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (payload['name'], payload['email']))
        elif op == 'read_user':
            cursor.execute("SELECT * FROM users WHERE name = %s", (payload['filter_name'],))
            result = cursor.fetchall()
            response = json.dumps(result)
        elif op == 'update_user':
            cursor.execute("UPDATE users SET name = %s, email = %s WHERE name = %s",
                           (payload['new_name'], payload['new_email'], payload['filter_name']))
        elif op == 'delete_user':
            cursor.execute("DELETE FROM users WHERE name = %s", (payload['filter_name'],))
        elif op == 'join_users_and_orders':
            cursor.execute("""
                SELECT users.name, orders.product
                FROM users JOIN orders ON users.id = orders.user_id
            """)
            result = cursor.fetchall()
            response = json.dumps(result)
        elif op == 'aggregate_users':
            method = payload['method'].upper()
            if method in ['COUNT', 'AVG', 'SUM', 'DISTINCT']:
                query = f"SELECT {method}(id) FROM users"
                cursor.execute(query)
                response = json.dumps(cursor.fetchone())
        else:
            response = 'Operación no válida'

        conn.commit()
        if not response:
            response = 'OK'
    except Exception as e:
        response = f"Error: {str(e)}"
        conn.rollback()

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
channel.queue_declare(queue='sql_queue')
channel.basic_consume(queue='sql_queue', on_message_callback=handle_message)
print("[SQL] Esperando mensajes...")
channel.start_consuming()
'''

'''
import pika
import json
import psycopg2

# Configuración DB PostgreSQL
conn = psycopg2.connect(
    dbname="test_db", user="postgres", password="1234", host="localhost", port="5432"
)
cursor = conn.cursor()

# Conexión RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="db_rpc_queue")

def handle_sql_operation(operation, payload):
    try:
        if operation == "CREATE":
            cursor.execute(payload["query"])
        elif operation == "READ":
            cursor.execute(payload["query"])
            result = cursor.fetchall()
            return {"result": result}
        elif operation == "UPDATE":
            cursor.execute(payload["query"])
        elif operation == "DELETE":
            cursor.execute(payload["query"])
        elif operation == "JOIN":
            cursor.execute(payload["query"])
            result = cursor.fetchall()
            return {"result": result}
        elif operation == "AGGREGATE":
            cursor.execute(payload["query"])
            result = cursor.fetchone()
            return {"result": result}
        else:
            return {"error": "Operación SQL no reconocida"}

        conn.commit()
        return {"status": "ok"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

def handle_sql_operation(operation, payload):
    dbname = payload.get("dbname", "postgres")  # Default a 'postgres'
    try:
        temp_conn = psycopg2.connect(
            dbname=dbname, user="postgres", password="1234", host="localhost", port="5432"
        )
        temp_cursor = temp_conn.cursor()

        if operation == "CREATE":
            temp_cursor.execute(payload["query"])
        elif operation == "READ":
            temp_cursor.execute(payload["query"])
            result = temp_cursor.fetchall()
            return {"result": result}
        elif operation == "UPDATE":
            temp_cursor.execute(payload["query"])
        elif operation == "DELETE":
            temp_cursor.execute(payload["query"])
        elif operation == "JOIN":
            temp_cursor.execute(payload["query"])
            result = temp_cursor.fetchall()
            return {"result": result}
        elif operation == "AGGREGATE":
            temp_cursor.execute(payload["query"])
            result = temp_cursor.fetchone()
            return {"result": result}
        else:
            return {"error": "Operación SQL no reconocida"}

        temp_conn.commit()
        return {"status": "ok"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'temp_cursor' in locals():
            temp_cursor.close()
        if 'temp_conn' in locals():
            temp_conn.close()

def on_request(ch, method, props, body):
    data = json.loads(body)
    if data["engine"] != "sql":
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    operation = data["operation"]
    payload = data["payload"]
    response = handle_sql_operation(operation, payload)

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(response)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

print("[SQL SERVICE] Esperando mensajes...")
channel.basic_consume(queue="db_rpc_queue", on_message_callback=on_request)
channel.start_consuming()
'''
from flask import Flask, request, jsonify
import psycopg2
import pika
import json

app = Flask(__name__)

def handle_sql_operation(operation, payload):
    dbname = payload.get("dbname", "postgres")  # Por defecto usa 'postgres'

    try:
        # Conexión dinámica
        temp_conn = psycopg2.connect(
            dbname=dbname, user="postgres", password="1234", host="localhost", port="5432"
        )
        temp_cursor = temp_conn.cursor()

        query = payload.get("query", "")
        if not query:
            return {"error": "No se proporcionó ninguna consulta SQL"}

        if operation in ["CREATE", "UPDATE", "DELETE"]:
            temp_cursor.execute(query)
            temp_conn.commit()
            return {"status": "ok"}

        elif operation in ["READ", "JOIN"]:
            temp_cursor.execute(query)
            result = temp_cursor.fetchall()
            return {"result": result}

        elif operation == "AGGREGATE":
            temp_cursor.execute(query)
            result = temp_cursor.fetchone()
            return {"result": result}

        else:
            return {"error": "Operación SQL no reconocida"}

    except Exception as e:
        return {"error": str(e)}
    finally:
        if 'temp_cursor' in locals():
            temp_cursor.close()
        if 'temp_conn' in locals():
            temp_conn.close()

def callback(ch, method, properties, body):
    message = json.loads(body)
    operation = message.get("operation")
    payload = message.get("payload", {})

    response = handle_sql_operation(operation, payload)

    # Enviar la respuesta por la cola de retorno
    if properties.reply_to:
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=json.dumps(response)
        )

channel = pika.BlockingConnection(pika.ConnectionParameters("localhost")).channel()
channel.queue_declare(queue="sql_queue")
channel.basic_consume(queue="sql_queue", on_message_callback=callback, auto_ack=True)

print(" [*] Esperando mensajes de SQL. Para salir presiona CTRL+C")
channel.start_consuming()
