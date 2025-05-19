import pika
import uuid
import json

class RPCClient:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()

        # Cola exclusiva y temporal para respuestas
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.response = None
        self.corr_id = None

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, queue, message):
        self.response = None
        self.corr_id = str(uuid.uuid4())

        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
                content_type='application/json'
            ),
            body=json.dumps(message)
        )

        while self.response is None:
            self.connection.process_data_events()  # Espera por la respuesta

        return self.response.decode()

if __name__ == "__main__":
    rpc_client = RPCClient()

    message = {
        "operation": "update_user",
        "payload": {"id": 1, "name": "Juan Actualizado RPC", "email": "juan.rpc@example.com"}
    }
    response = rpc_client.call("sql_queue", message)
    print("Respuesta del servidor SQL:", response)

    message = {
        "operation": "delete_user",
        "payload": {"name": "Ana RPC"}
    }
    response = rpc_client.call("nosql_queue", message)
    print("Respuesta del servidor NoSQL:", response)
