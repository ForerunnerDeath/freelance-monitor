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
