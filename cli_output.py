from logger import log_info


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
        print("Поставлено в очередь Telegram:", stats.get("telegram_queued", 0))
        print("Ошибок Telegram:", stats.get("telegram_failed", 0))


def print_stats(result):
    total_count = result.get("total", "")
    duplicate_count = result.get("duplicates", "")
    matched_count = result.get("matched", "")
    rejected_count = result.get("rejected", "")
    risky_count = result.get("risky", "")
    telegram_sent_count = result.get("telegram_sent", "")
    telegram_failed_count = result.get("telegram_failed", "")
    telegram_queued_count = result.get("telegram_queued", "")
    print("-----")
    print("Статистика:")
    print("Всего заказов:", total_count)
    print("Дублей:", duplicate_count)
    print("Подходящих:", matched_count)
    print("Неподходящих:", rejected_count)
    print("Рискованных:", risky_count)
    print("Поставлено в очередь Telegram:", telegram_queued_count)
    print("Отправлено в Telegram:", telegram_sent_count)
    print("Ошибка отправления в Telegram:", telegram_failed_count)


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
