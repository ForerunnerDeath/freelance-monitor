import filters
from sources import fl_ru
import db
import telegram_notify

def process_orders(orders):

    total_count = 0
    duplicate_count = 0
    matched_count = 0
    rejected_count = 0

    matched_orders = []
    rejected_orders = []

    for order in orders:
        total_count += 1
        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")

        if db.is_order_seen(source, external_id):
            duplicate_count += 1
            print("Дубль заказа", source, external_id, title)
            continue

        check_result = filters.check_order_v2(order)
        status = check_result.get("status")
        reason = check_result.get("reason")
        matched_keyword = check_result.get("matched_keyword")
        negative_keyword = check_result.get("negative_keyword")


        if status == "matched":
            db_status = "matched"

            matched_count += 1
            matched_orders.append(order)
            print("Подходящий заказ", source, external_id, title, "Ключ: ", matched_keyword)
            telegram_notify.notify_about_order(order, check_result)
        else:
            db_status = "rejected"

            rejected_count += 1
            rejected_orders.append({
                "order": order,
                "reason": reason,
            })
            if negative_keyword is not None:
                print("Не подходит", source, external_id, title, "Причина:", reason, "Минус-слово: ", negative_keyword)
            else:
                print("Не подходит", source, external_id, title, "Причина:", reason)

        db.save_order(order, db_status, reason)

    print()
    print("Статистика:")
    print("Всего заказов:", total_count)
    print("Дублей:", duplicate_count)
    print("Подходящих:", matched_count)
    print("Неподходящих:", rejected_count)

    return {
        "total": total_count,
        "duplicates": duplicate_count,
        "matched": matched_count,
        "rejected": rejected_count,
        "matched_orders": matched_orders,
        "rejected_orders": rejected_orders,
    }


def print_matched_orders(result):
    print()
    print("Подходящие заказы в result:")

    for order in result["matched_orders"]:
        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")
        budget = order.get("budget", 0)

        print(source, external_id, title, "Бюджет:", budget)


def print_rejected_orders(result):
    print()
    print("Неподходящие заказы в result:")

    for rejected_item in result["rejected_orders"]:
        order = rejected_item["order"]
        reason = rejected_item["reason"]
        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")

        print(source, external_id, title, "Причина:", reason)

def get_orders():
    return fl_ru.fetch_orders()


def main():
    db.init_db()
    orders = get_orders()
    result = process_orders(orders)
    print_matched_orders(result)
    print_rejected_orders(result)


if __name__ == "__main__":
    main()