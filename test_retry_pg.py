from uuid import uuid4

from database import SessionLocal
from main import process_orders_pg


external_id = f"rejected-{uuid4()}"

test_order = {
    "source": "test_process_pg",
    "external_id": external_id,
    "title": "Сделать парсер сайта",
    "url": "https://example.com/test-process-pg",
    "description": "Нужно сделать простой парсинг сайта, но бюджет слишком маленький",
    "budget": "500",
    "project_type": "project",
    "tags": [],
}

orders = [test_order]


with SessionLocal() as session:
    print("----- FIRST RUN -----")
    first_result = process_orders_pg(orders, session, verbose=True)
    print(first_result)

    print()
    print("----- SECOND RUN / DUPLICATE CHECK -----")
    second_result = process_orders_pg(orders, session, verbose=True)
    print(second_result)