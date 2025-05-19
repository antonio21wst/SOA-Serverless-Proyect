# crud_service/handlers/nosql_handler.py
from pymongo import MongoClient

def handle_nosql_message(message):
    operation = message.get("operation")
    payload = message.get("payload")

    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_nosql"]
    collection = db["users"]

    try:
        if operation == "insert_user":
            collection.insert_one(payload)
            return {"status": "success", "message": "Documento insertado"}


        elif operation == "get_users":
            users = list(collection.find({}, {"_id": 0}))
            print("Usuarios MongoDB:", users)

        elif operation == "update_user":
            # Espera payload con filtro y actualización
            filter_ = {"name": payload["filter_name"]}
            new_values = {"$set": {"name": payload["new_name"], "email": payload["new_email"]}}
            result = collection.update_one(filter_, new_values)
            return {"status": "success", "message": f"Documentos actualizados: {result.modified_count}"}


        elif operation == "delete_user":
            # Espera payload con filtro para borrar
            filter_ = {"name": payload["name"]}
            result = collection.delete_one(filter_)
            print(f"Eliminados: {result.deleted_count}")
            return {"status": "success", "message": f"Documentos eliminados: {result.deleted_count}"}

        # Otros handlers...

    except Exception as e:
        print(f"[Mongo Handler Error] {e}")

    finally:
        client.close()
