# crud_service/sql_crud_service.py
import pika
import psycopg2
import json

def process_sql_crud(message):
    data = json.loads(message)
    operation = data.get("operation")
    payload = data.get("payload")

    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    if operation == "insert_user":
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)",
                       (payload["name"], payload["email"]))
        conn.commit()

    elif operation == "get_users":
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
        print("Usuarios:", result)

    cursor.close()
    conn.close()


# RabbitMQ listener
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='sql_queue')

def callback(ch, method, properties, body):
    print("[SQL] Mensaje recibido:", body.decode())
    process_sql_crud(body.decode())

channel.basic_consume(queue='sql_queue', on_message_callback=callback, auto_ack=True)

print("[SQL] Esperando mensajes SQL...")
channel.start_consuming()
