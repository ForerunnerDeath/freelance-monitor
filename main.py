import sys
import time

import config
from cli_output import (print_matched_orders, print_rejected_orders,
                        print_risky_orders, print_source_stats, print_stats)
from database import SessionLocal
from logger import log_error, log_info
from services.order_service import process_orders
from services.source_service import get_orders


def log_stats(result):
    total_count = result.get("total", "")
    duplicate_count = result.get("duplicates", "")
    matched_count = result.get("matched", "")
    rejected_count = result.get("rejected", "")
    risky_count = result.get("risky", "")
    telegram_sent_count = result.get("telegram_sent")
    telegram_failed_count = result.get("telegram_failed")
    telegram_queued_count = result.get("telegram_queued")

    log_info(
        f"Статистика: всего {total_count}, дублей {duplicate_count}, "
        f"подходящих {matched_count}, неподходящих {rejected_count}, "
        f"рискованных {risky_count}, отправлено в TG {telegram_sent_count}, "
        f"поставлено в очередь TG {telegram_queued_count}, "
        f"ошибок отправки в TG {telegram_failed_count}"
    )


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
        telegram_queued = stats.get("telegram_queued", 0)
        log_info(
            f"Источники: {source}, всего {total_count}, дублей {duplicates}, "
            f"подходящих {matched}, неподходящих {rejected}, "
            f"рискованных {risky}, отправлено в TG {telegram_sent}, "
            f"поставлено в очередь TG {telegram_queued}, "
            f"ошибок отправки в TG {telegram_failed}"
        )


def run_once(verbose=True):
    log_info("Старт проверки заказов")
    with SessionLocal() as session:
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
