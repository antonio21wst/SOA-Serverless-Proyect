# soap_gateway/server.py
from spyne import Application, rpc, ServiceBase, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import pika, json

def send_to_queue(queue, payload):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(exchange='', routing_key=queue, body=json.dumps(payload))
    connection.close()

class DBService(ServiceBase):

    @rpc(Unicode, _returns=Unicode)
    def createSQLDatabase(ctx, dbname):
        payload = {"action": "create_db", "dbname": dbname}
        send_to_queue("sql_db_queue", payload)
        return f"Base de datos SQL '{dbname}' enviada para creación"

    @rpc(Unicode, Unicode, _returns=Unicode)
    def createSQLTable(ctx, dbname, table_sql):
        payload = {"action": "create_table", "dbname": dbname, "table_sql": table_sql}
        send_to_queue("sql_db_queue", payload)
        return f"Tabla enviada para creación en '{dbname}'"

    @rpc(Unicode, Unicode, _returns=Unicode)
    def createNoSQLCollection(ctx, dbname, collection):
        payload = {"dbname": dbname, "collection": collection}
        send_to_queue("nosql_db_queue", payload)
        return f"Colección '{collection}' enviada para creación en MongoDB"
    # CREATE (SQL)
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def insertSQL(ctx, dbname, table, values_sql):
        payload = {"action": "insert", "dbname": dbname, "table": table, "query": values_sql}
        send_to_queue("sql_crud_queue", payload)
        return f"Insert enviado a tabla '{table}'"

    # READ (SQL)
    @rpc(Unicode, Unicode, _returns=Unicode)
    def querySQL(ctx, dbname, query):
        payload = {"action": "select", "dbname": dbname, "query": query}
        send_to_queue("sql_crud_queue", payload)
        return f"Consulta enviada: {query}"

    # UPDATE (SQL)
    @rpc(Unicode, Unicode, _returns=Unicode)
    def updateSQL(ctx, dbname, query):
        payload = {"action": "update", "dbname": dbname, "query": query}
        send_to_queue("sql_crud_queue", payload)
        return f"Actualización enviada: {query}"

    # DELETE (SQL)
    @rpc(Unicode, Unicode, _returns=Unicode)
    def deleteSQL(ctx, dbname, query):
        payload = {"action": "delete", "dbname": dbname, "query": query}
        send_to_queue("sql_crud_queue", payload)
        return f"Eliminación enviada: {query}"

    # INSERT (MongoDB)
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def insertNoSQL(ctx, dbname, collection, json_doc):
        payload = {"action": "insert", "dbname": dbname, "collection": collection, "document": json_doc}
        send_to_queue("nosql_crud_queue", payload)
        return f"Documento enviado a '{collection}'"

    # READ (MongoDB)
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def findNoSQL(ctx, dbname, collection, filter_json):
        payload = {"action": "find", "dbname": dbname, "collection": collection, "filter": filter_json}
        send_to_queue("nosql_crud_queue", payload)
        return f"Búsqueda en colección '{collection}' enviada"

    # UPDATE (MongoDB)
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def updateNoSQL(ctx, dbname, collection, filter_json, update_json):
        payload = {
            "action": "update", "dbname": dbname, "collection": collection,
            "filter": filter_json, "update": update_json
        }
        send_to_queue("nosql_crud_queue", payload)
        return f"Actualización enviada en colección '{collection}'"

    # DELETE (MongoDB)
    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def deleteNoSQL(ctx, dbname, collection, filter_json):
        payload = {"action": "delete", "dbname": dbname, "collection": collection, "filter": filter_json}
        send_to_queue("nosql_crud_queue", payload)
        return f"Eliminación en '{collection}' enviada"
    
# Definición de la aplicación SOAP
app = Application(
    [DBService],
    tns='soap.dbservice',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11()
)

wsgi_app = WsgiApplication(app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print("SOAP DBService corriendo en http://localhost:8000")
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
