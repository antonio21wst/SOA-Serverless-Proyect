from spyne import Application, rpc, ServiceBase, Unicode, Integer, ComplexModel, Array
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import json
from producer import RPCClient

rpc_sql = RPCClient()
rpc_nosql = RPCClient()

class SQLPayload(ComplexModel):
    filter_name = Unicode
    new_name = Unicode
    new_email = Unicode

class MongoPayload(ComplexModel):
    collection = Unicode
    filters = Unicode
    updates = Unicode
    document = Unicode
    pipeline = Unicode

class CrudService(ServiceBase):

    @rpc(Unicode, Unicode, Unicode, _returns=Unicode)
    def create_user(ctx, name, email):
        message = {
            "operation": "create_user",
            "payload": {"name": name, "email": email}
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(Unicode, _returns=Unicode)
    def read_user(ctx, filter_name):
        message = {
            "operation": "read_user",
            "payload": {"filter_name": filter_name}
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(SQLPayload, _returns=Unicode)
    def update_user(ctx, payload):
        message = {
            "operation": "update_user",
            "payload": payload.__dict__
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(Unicode, _returns=Unicode)
    def delete_user(ctx, filter_name):
        message = {
            "operation": "delete_user",
            "payload": {"filter_name": filter_name}
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(_returns=Unicode)
    def join_users_and_orders(ctx):
        message = {
            "operation": "join_users_and_orders",
            "payload": {}
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(Unicode, _returns=Unicode)
    def aggregate_users(ctx, method):
        message = {
            "operation": "aggregate_users",
            "payload": {"method": method}
        }
        return rpc_sql.call("sql_queue", message)

    @rpc(MongoPayload, _returns=Unicode)
    def nosql_insert(ctx, payload):
        message = {
            "operation": "nosql_insert",
            "payload": {
                "collection": payload.collection,
                "document": json.loads(payload.document)
            }
        }
        return rpc_nosql.call("nosql_queue", message)

    @rpc(MongoPayload, _returns=Unicode)
    def nosql_read(ctx, payload):
        message = {
            "operation": "nosql_read",
            "payload": {
                "collection": payload.collection,
                "filters": json.loads(payload.filters)
            }
        }
        return rpc_nosql.call("nosql_queue", message)

    @rpc(MongoPayload, _returns=Unicode)
    def nosql_update(ctx, payload):
        message = {
            "operation": "nosql_update",
            "payload": {
                "collection": payload.collection,
                "filters": json.loads(payload.filters),
                "updates": json.loads(payload.updates)
            }
        }
        return rpc_nosql.call("nosql_queue", message)

    @rpc(MongoPayload, _returns=Unicode)
    def nosql_delete(ctx, payload):
        message = {
            "operation": "nosql_delete",
            "payload": {
                "collection": payload.collection,
                "filters": json.loads(payload.filters)
            }
        }
        return rpc_nosql.call("nosql_queue", message)

    @rpc(MongoPayload, _returns=Unicode)
    def nosql_aggregate(ctx, payload):
        message = {
            "operation": "nosql_aggregate",
            "payload": {
                "collection": payload.collection,
                "pipeline": json.loads(payload.pipeline)
            }
        }
        return rpc_nosql.call("nosql_queue", message)

application = Application([CrudService],
                          tns='soa.database.service',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    print("SOAP en http://localhost:8000/?wsdl")
    make_server('0.0.0.0', 8000, wsgi_app).serve_forever()
