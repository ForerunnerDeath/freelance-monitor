from uuid import uuid4

from database import SessionLocal
from db_sqlalchemy import (
    save_order,
    get_order_by_source_and_external_id,
    get_all_orders,
    get_all_orders_as_dicts,
    get_order_by_source_and_external_id_as_dict,
    update_order_contacted_as_dict,
    mark_order_sent_to_telegram,
    get_unsent_telegram_orders,
    get_unsent_telegram_orders_as_dicts,
    is_order_seen,
)


external_id = f"test-{uuid4()}"

order_data = {
    "source": "test_source",
    "external_id": external_id,
    "title": "Тестовый заказ SQLAlchemy",
    "url": f"https://example.com/order/{external_id}",
    "description": "Описание тестового заказа",
    "budget": "10000 руб",
    "project_type": "project",
}

check_result = {
    "status": "matched",
    "reason": "good_keyword",
    "budget": 10000,
    "matched_keyword": "python",
    "negative_keyword": None,
    "risky_keyword": None,
}


with SessionLocal() as session:
    existing = is_order_seen(session, "test_source", "test-1")
    print("existing seen:", existing)

    missing = is_order_seen(session, "test_source", "not-exists")
    print("missing seen:", missing)