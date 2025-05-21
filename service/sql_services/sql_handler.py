# sql_handler.py
import psycopg2

def handle_sql_operation(operation, payload):
    dbname = payload.get("dbname", "postgres") 
    query = payload.get("query", "")
    if not query:
        return {"error": "No se proporcionó ninguna consulta SQL"}

    try:
        if "create database" in query.lower():
            conn = psycopg2.connect(
                dbname="postgres", user="postgres", password="1234", host="localhost", port="5432"
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(query)
            return {"status": "Base de datos creada correctamente"}
        else:
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
