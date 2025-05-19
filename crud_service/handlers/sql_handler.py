# crud_service/handlers/sql_handler.py
import psycopg2

def handle_sql_message(message):
    operation = message.get("operation")
    payload = message.get("payload")

    conn = psycopg2.connect(
        dbname="test_db",
        user="postgres",
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()

    try:
        if operation == "insert_user":
            cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)",
                           (payload["name"], payload["email"]))
            conn.commit()
            return {"status": "success", "message": "Usuario insertado"}

        elif operation == "get_users":
            cursor.execute("SELECT * FROM users")
            result = cursor.fetchall()
            print("Usuarios:", result)
            
        elif operation == "update_user":
            # Espera payload con id, name y email para actualizar
            cursor.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (payload["name"], payload["email"], payload["id"])
            )
            conn.commit()
            return {"status": "success", "message": f"Usuario {payload['id']} actualizado"}

        elif operation == "delete_user":
            # Espera payload con id para eliminar
            cursor.execute("DELETE FROM users WHERE id = %s", (payload["id"],))
            conn.commit()
            return {"status": "success", "message": f"Usuario {payload['id']} eliminado"}
        # Otros handlers...

    except Exception as e:
        print(f"[SQL Handler Error] {e}")

    finally:
        cursor.close()
        conn.close()
