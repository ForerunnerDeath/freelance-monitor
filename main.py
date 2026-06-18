import sys
import time
from database import SessionLocal

import config
from services.order_service import process_orders, retry_unsent_telegram_orders
from cli_output import print_source_stats, print_stats, print_matched_orders, print_rejected_orders, print_risky_orders
from logger import log_info, log_error
from services.source_service import get_orders


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
