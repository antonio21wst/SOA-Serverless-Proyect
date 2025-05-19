# crud_service/sql_crud_service.py
from base_service import CRUDServiceBase
from handlers.sql_handler import handle_sql_message

if __name__ == "__main__":
    service = CRUDServiceBase(queue_name="sql_queue", handler_function=handle_sql_message)
    service.start()
