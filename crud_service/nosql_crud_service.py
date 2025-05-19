# crud_service/nosql_crud_service.py
from base_service import CRUDServiceBase
from handlers.nosql_handler import handle_nosql_message

if __name__ == "__main__":
    service = CRUDServiceBase(queue_name="nosql_queue", handler_function=handle_nosql_message)
    service.start()
