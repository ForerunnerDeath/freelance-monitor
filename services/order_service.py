import db_sqlalchemy
import filters
import telegram_notify


def process_orders(orders, session, verbose=True):

    total_count = 0
    duplicate_count = 0
    matched_count = 0
    rejected_count = 0
    risky_count = 0
    telegram_sent_count = 0
    telegram_failed_count = 0

    matched_orders = []
    rejected_orders = []
    risky_orders = []
    source_stats = {}

    for order in orders:
        total_count += 1
        source = order.get("source", "")

        if source not in source_stats:
            source_stats[source] = {
                "total": 0,
                "duplicates": 0,
                "matched": 0,
                "risky": 0,
                "rejected": 0,
                "telegram_sent": 0,
                "telegram_failed": 0,
            }
        source_stats[source]["total"] += 1

        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")

        if db_sqlalchemy.is_order_seen(session, source, external_id):
            duplicate_count += 1
            source_stats[source]["duplicates"] += 1
            if verbose:
                print("Дубль заказа", source, external_id, title)
            continue

        check_result = filters.check_order_v2(order)
        status = check_result.get("status")
        reason = check_result.get("reason")
        matched_keyword = check_result.get("matched_keyword")
        negative_keyword = check_result.get("negative_keyword")
        risky_keyword = check_result.get("risky_keyword")

        if status == "matched":
            matched_count += 1
            source_stats[source]["matched"] += 1
            matched_orders.append(order)
            if verbose:
                print("Подходящий заказ", source, external_id, title, "Ключ: ", matched_keyword)
        elif status == "risky":
            risky_count += 1
            source_stats[source]["risky"] += 1
            risky_orders.append({
                "order": order,
                "risky_keyword": risky_keyword,
            })
            if verbose:
                print("Рискованный заказ", source, external_id, title, "Ключ:", risky_keyword)
        else:
            rejected_count += 1
            source_stats[source]["rejected"] += 1
            rejected_orders.append({
                "order": order,
                "reason": reason,
            })
            if negative_keyword is not None:
                if verbose:
                    print("Не подходит", source, external_id, title, "Причина:", reason, "Минус-слово: ", negative_keyword)
            else:
                if verbose:
                    print("Не подходит", source, external_id, title, "Причина:", reason)
        db_sqlalchemy.save_order(session, order, check_result, sent_to_telegram=False)

        if status in ("matched", "risky"):
            telegram_sent = telegram_notify.notify_about_order(order, check_result)
            if telegram_sent:
                marked = db_sqlalchemy.mark_order_sent_to_telegram(session, source, external_id)
                if marked:
                    telegram_sent_count += 1
                    source_stats[source]["telegram_sent"] += 1
                else:
                    telegram_failed_count += 1
                    source_stats[source]["telegram_failed"] += 1
            else:
                telegram_failed_count += 1
                source_stats[source]["telegram_failed"] += 1

    return {
        "total": total_count,
        "duplicates": duplicate_count,
        "matched": matched_count,
        "rejected": rejected_count,
        "matched_orders": matched_orders,
        "rejected_orders": rejected_orders,
        "risky": risky_count,
        "risky_orders": risky_orders,
        "telegram_sent": telegram_sent_count,
        "telegram_failed": telegram_failed_count,
        "source_stats": source_stats,
    }