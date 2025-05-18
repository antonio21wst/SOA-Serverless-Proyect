# messaging_service/consumer.py
import pika

# Conexión a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Asegurarse de que la cola existe
channel.queue_declare(queue='test_queue')

# Función callback que maneja los mensajes recibidos
def callback(ch, method, properties, body):
    print(f"[x] Mensaje recibido: {body.decode()}")

# Consumir mensajes
channel.basic_consume(queue='test_queue',
                      on_message_callback=callback,
                      auto_ack=True)

print("[*] Esperando mensajes. Presiona Ctrl+C para salir.")
channel.start_consuming()
