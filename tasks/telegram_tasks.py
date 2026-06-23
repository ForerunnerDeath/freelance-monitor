from database import SessionLocal
from services.order_service import send_telegram_for_saved_order


def send_telegram_for_order_task(source, external_id):
    session = SessionLocal()

    try:
        result = send_telegram_for_saved_order(session, source, external_id)

        if result["status"] == "failed":
            reason = result.get("reason", "unknown_error")
            raise RuntimeError(reason)
        return result
    finally:
        session.close()