import filters
from sources import fl_ru
import db
import telegram_notify
import time
import datetime
import sys
import config

def process_orders(orders, verbose=True):

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

    for order in orders:
        total_count += 1
        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")

        if db.is_order_seen(source, external_id):
            duplicate_count += 1
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
            matched_orders.append(order)
            if verbose:
                print("Подходящий заказ", source, external_id, title, "Ключ: ", matched_keyword)
        elif status == "risky":
            risky_count += 1
            risky_orders.append({
                "order": order,
                "risky_keyword": risky_keyword,
            })
            if verbose:
                print("Рискованный заказ", source, external_id, title, "Ключ:", risky_keyword)
        else:
            rejected_count += 1
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
        db.save_order(order, check_result, sent_to_telegram=0)

        if status in ("matched", "risky"):
            telegram_sent = telegram_notify.notify_about_order(order, check_result)
            if telegram_sent:
                db.mark_order_sent_to_telegram(source, external_id)
                telegram_sent_count += 1
            else:
                telegram_failed_count += 1

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
    }

def print_stats(result):
    total_count = result.get("total", "")
    duplicate_count = result.get("duplicates", "")
    matched_count = result.get("matched", "")
    rejected_count = result.get("rejected", "")
    risky_count = result.get("risky", "")
    telegram_sent_count = result.get("telegram_sent", "")
    telegram_failed_count = result.get("telegram_failed", "")
    print("-----")
    print("Статистика:")
    print("Всего заказов:", total_count)
    print("Дублей:", duplicate_count)
    print("Подходящих:", matched_count)
    print("Неподходящих:", rejected_count)
    print("Рискованных:", risky_count)
    print("Отправлено в Telegram:", telegram_sent_count)
    print("Ошибка отправления в Telegram:", telegram_failed_count)

def log_stats(result):
    total_count = result.get("total", "")
    duplicate_count = result.get("duplicates", "")
    matched_count = result.get("matched", "")
    rejected_count = result.get("rejected", "")
    risky_count = result.get("risky", "")
    telegram_sent_count = result.get("telegram_sent")
    telegram_failed_count = result.get("telegram_failed")

    log_info(f"Статистика: всего {total_count}, дублей {duplicate_count}, подходящих {matched_count}, неподходящих {rejected_count}, рискованных {risky_count}, отправлено в TG {telegram_sent_count}, ошибок отправки в TG {telegram_failed_count}")    

def print_matched_orders(result):
    print()
    print("Подходящие заказы в result:")

    for order in result["matched_orders"]:
        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")
        budget = order.get("budget", 0)
        description = order.get("description", "")

        print("-----")
        print(source, external_id, title)
        print("Бюджет:", budget)
        print("Описание:", description)


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

def print_risky_orders(result):
    print()
    print("Рискованные заказы в result:")

    for risky_item in result["risky_orders"]:
        order = risky_item["order"]
        risky_keyword = risky_item["risky_keyword"]

        source = order.get("source", "")
        external_id = str(order.get("external_id", ""))
        title = order.get("title", "Без названия")
        budget = order.get("budget", 0)
        description = order.get("description", "")

        print("-----")
        print(source, external_id, title)
        print("Бюджет:", budget)
        print("Риск-слово:", risky_keyword)
        print("Описание:", description)

def retry_unsent_telegram_orders():
    unsent_orders = db.get_unsent_telegram_orders()
    sent_count = 0
    failed_count = 0

    for saved_order in unsent_orders:
        order = {
            "source": saved_order.get("source", ""),
            "external_id": saved_order.get("external_id", ""),
            "title": saved_order.get("title", ""),
            "url": saved_order.get("url", ""),
            "description": saved_order.get("description", ""),
            "budget": saved_order.get("budget", ""),
            "tags": [],
        }
        check_result = {
            "status": saved_order.get("status", ""),
            "reason": saved_order.get("reason", ""),
            "budget": saved_order.get("parsed_budget", ""),
            "matched_keyword": saved_order.get("matched_keyword", ""),
            "negative_keyword": saved_order.get("negative_keyword", ""),
            "risky_keyword": saved_order.get("risky_keyword", ""),
        }

        telegram_sent = telegram_notify.notify_about_order(order, check_result)
        if telegram_sent:
            marked = db.mark_order_sent_to_telegram(
                saved_order.get("source", ""),
                saved_order.get("external_id", "")
            )
            if marked:
                sent_count += 1
            else:
                failed_count += 1
        else:
            failed_count += 1
    return {
        "total": len(unsent_orders),
        "sent": sent_count,
        "failed": failed_count,
    }

def get_orders(verbose):
    return fl_ru.fetch_orders(pages=config.FL_RU_PAGES, verbose=verbose)


def run_once(verbose=True):
    log_info("Старт проверки заказов")
    db.init_db()
    retry_result = retry_unsent_telegram_orders()
    retry_total = retry_result["total"]
    retry_sent = retry_result["sent"]
    retry_failed = retry_result["failed"]
    if retry_total > 0:
        log_info(f"Повторная отправка Telegram: найдено {retry_total}, отправлено {retry_sent}, ошибок {retry_failed}")
    orders = get_orders(verbose)
    log_info(f"Получено заказов: {len(orders)}")
    result = process_orders(orders, verbose=verbose)
    if verbose:
        print_stats(result)
        print_matched_orders(result)
        print_risky_orders(result)
        print_rejected_orders(result)
    else:
        log_stats(result)
    log_info("Проверка заказов завершена")

def log_info(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] INFO: {message}")

def log_error(message):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] ERROR: {message}")

def main():
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "once"
    if len(sys.argv) > 2:
        try:
            interval = int(sys.argv[2])
        except ValueError:
            log_error("Интервал должен быть числом секунд")
            return
    else:
        interval = config.DEFAULT_INTERVAL
        
    if mode == "watch" and interval < config.MIN_INTERVAL:
        log_error(f"Интервал не может быть меньше {config.MIN_INTERVAL} секунд")
        return

    if mode == "once":    
        try:
            run_once(verbose=True)
        except Exception as error:
            log_error(str(error))
    elif mode == "watch":
        while True:
            try:
                run_once(verbose=False)
            except Exception as error:
                log_error(str(error))     
            log_info(f"Пауза {interval} секунд...")
            time.sleep(interval)
    else:
        log_error("Неизвестный режим. Используй: once или watch")
        
if __name__ == "__main__":
    main()
    