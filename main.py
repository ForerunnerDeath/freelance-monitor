import datetime
import sys
import time
from database import SessionLocal

import config
from sources import fl_ru, profi_ru
from services.order_service import process_orders, retry_unsent_telegram_orders


def print_source_stats(result):
    source_stats = result.get("source_stats", {})
    print()
    print("Статистика по источникам:")

    for source, stats in source_stats.items():
        print("-----")
        print("Источник:", source)
        print("Всего:", stats.get("total", 0))
        print("Дублей:", stats.get("duplicates", 0))
        print("Подходящих:", stats.get("matched", 0))
        print("Рискованных:", stats.get("risky", 0))
        print("Неподходящих:", stats.get("rejected", 0))
        print("Отправлено в Telegram:", stats.get("telegram_sent", 0))
        print("Ошибок Telegram:", stats.get("telegram_failed", 0))


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


def log_source_stats(result):
    source_stats = result.get("source_stats", {})
    for source, stats in source_stats.items():
        total_count = stats.get("total", 0)
        duplicates = stats.get("duplicates", 0)
        matched = stats.get("matched", 0)
        risky = stats.get("risky", 0)
        rejected = stats.get("rejected", 0)
        telegram_sent = stats.get("telegram_sent", 0)
        telegram_failed = stats.get("telegram_failed", 0)
        log_info(f"Источники: {source}, всего {total_count}, дублей {duplicates}, подходящих {matched}, неподходящих {rejected}, рискованных {risky}, отправлено в TG {telegram_sent}, ошибок отправки в TG {telegram_failed}")


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


def get_orders(verbose):
    all_orders = []
    source_modules = []
    if config.ENABLE_FL_RU:
        source_modules.append(fl_ru)
    if config.ENABLE_PROFI_RU:
        source_modules.append(profi_ru)
    for source_module in source_modules:
        try:
            if source_module == fl_ru:
                pages = config.FL_RU_PAGES
            if source_module == profi_ru:
                pages = config.PROFI_RU_PAGES
            source_orders = source_module.fetch_orders(pages=pages, verbose=verbose)
        except Exception as error:
            log_error(f"Ошибка получения заказов из {source_module.__name__}: {error}")
            continue
        if verbose:
            print("Источник", source_module.__name__, "вернул", len(source_orders), "заказов")
        all_orders.extend(source_orders)
    return all_orders


def run_once(verbose=True):
    log_info("Старт проверки заказов")
    with SessionLocal() as session:
        retry_result = retry_unsent_telegram_orders(session)
        retry_total = retry_result["total"]
        retry_sent = retry_result["sent"]
        retry_failed = retry_result["failed"]
        if retry_total > 0:
            log_info(f"Повторная отправка Telegram: найдено {retry_total}, отправлено {retry_sent}, ошибок {retry_failed}")
        orders = get_orders(verbose)
        log_info(f"Получено заказов: {len(orders)}")
        result = process_orders(orders, session, verbose=verbose)
    if verbose:
        print_stats(result)
        print_source_stats(result)
        print_matched_orders(result)
        print_risky_orders(result)
        print_rejected_orders(result)
    else:
        log_stats(result)
        log_source_stats(result)
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
