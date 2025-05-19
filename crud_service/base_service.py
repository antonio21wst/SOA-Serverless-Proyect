# crud_service/base_service.py
import pika
import json

class CRUDServiceBase:
    def __init__(self, queue_name, handler_function):
        self.queue_name = queue_name
        self.handler_function = handler_function
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)

    def start(self):
        print(f"[{self.queue_name}] Escuchando...")
        self.channel.basic_consume(queue=self.queue_name,
                                   on_message_callback=self.callback,
                                   auto_ack=False)  # Cambia a manual ack para controlar mejor
        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            print(f"[{self.queue_name}] Mensaje recibido: {message}")

            # Ejecuta el handler y obtiene respuesta (string)
            response = self.handler_function(message)

            # Envía la respuesta si se especifica cola reply_to
            if properties.reply_to:
                ch.basic_publish(
                    exchange='',
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                    body=json.dumps(response)
                )

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[ERROR] {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
