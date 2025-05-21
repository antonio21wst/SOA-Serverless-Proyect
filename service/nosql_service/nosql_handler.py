# nosql_handler.py
from pymongo import MongoClient

# Conexión MongoDB
client = MongoClient("mongodb://localhost:27017/")

def handle_nosql_operation(operation, payload):
    try:
        dbname = payload.get("dbname", "test")
        db = client[dbname]
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
