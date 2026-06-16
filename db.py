import sqlite3
import sys
from datetime import datetime

DB_NAME = "freelance_monitor.db"


def add_column_if_not_exists(cursor, table_name,
                             column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    existing_columns = []
    for column in columns:
        existing_columns.append(column[1])

    if column_name not in existing_columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT,
        external_id TEXT,
        title TEXT,
        url TEXT,
        description TEXT,
        budget TEXT,
        status TEXT,
        reason TEXT,
        created_at TEXT,
        UNIQUE(source, external_id)
    )
""")
    add_column_if_not_exists(cursor, "orders", "project_type", "TEXT")
    add_column_if_not_exists(cursor, "orders", "parsed_budget", "INTEGER")
    add_column_if_not_exists(cursor, "orders", "matched_keyword", "TEXT")
    add_column_if_not_exists(cursor, "orders", "negative_keyword", "TEXT")
    add_column_if_not_exists(cursor, "orders", "sent_to_telegram",
                             "INTEGER DEFAULT 0")
    add_column_if_not_exists(cursor, "orders", "risky_keyword", "TEXT")
    add_column_if_not_exists(cursor, "orders", "contacted",
                             "INTEGER DEFAULT 0")

    cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_orders_status_sent_to_telegram
            ON orders(status, sent_to_telegram)
            """)

    connection.commit()
    connection.close()


def is_order_seen(source, external_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1 FROM orders
        WHERE source = ? AND external_id = ?
        LIMIT 1
        """,
        (source, external_id)
    )

    row = cursor.fetchone()
    connection.close()

    return row is not None


def save_order(order, check_result, sent_to_telegram=0):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    source = order.get("source", "")
    external_id = str(order.get("external_id", ""))
    title = order.get("title", "Без названия")
    url = order.get("url", "")
    description = order.get("description", "")

    project_type = order.get("project_type", "")
    status = check_result.get("status", "")
    reason = check_result.get("reason", "")
    parsed_budget = check_result.get("budget", "")
    matched_keyword = check_result.get("matched_keyword", "")
    negative_keyword = check_result.get("negative_keyword", "")
    risky_keyword = check_result.get("risky_keyword", "")

    raw_budget = order.get("budget")
    if raw_budget is None:
        budget = ""
    else:
        budget = str(raw_budget)

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """
        INSERT OR IGNORE INTO orders (
            source,
            external_id,
            title,
            url,
            description,
            budget,
            status,
            reason,
            created_at,
            project_type,
            parsed_budget,
            matched_keyword,
            negative_keyword,
            risky_keyword,
            sent_to_telegram
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source,
            external_id,
            title,
            url,
            description,
            budget,
            status,
            reason,
            created_at,
            project_type,
            parsed_budget,
            matched_keyword,
            negative_keyword,
            risky_keyword,
            sent_to_telegram,
        )
    )

    connection.commit()
    connection.close()


def get_orders_count():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM orders"
    )

    row = cursor.fetchone()
    connection.close()
    return row[0]


def get_status_stats():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT status, COUNT(*) AS total
                   FROM orders
                   GROUP BY status
                   ORDER BY total DESC;
                   """)
    rows = cursor.fetchall()
    connection.close()

    stats = []

    for row in rows:
        status, total = row
        stats.append({
            "status": status,
            "total": total,
        })
    return stats


def print_status_stats():
    stats = get_status_stats()
    print("Статистика по статусам:")
    for item in stats:
        print(item["status"], item["total"])


def get_rejected_reason_stats():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT reason, COUNT(*) AS total
                   FROM orders
                   WHERE status = 'rejected'
                   GROUP BY reason
                   ORDER BY total DESC;
                   """)
    rows = cursor.fetchall()
    connection.close()

    stats = []

    for row in rows:
        reason, total = row
        stats.append({
            "reason": reason,
            "total": total,
        })
    return stats


def print_rejected_reason_stats():
    stats = get_rejected_reason_stats()
    print("Причины отказов:")
    for item in stats:
        print(item["reason"], item["total"])


def get_budget_quality_stats():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT status,
                   COUNT(*) AS total,
                   SUM(CASE WHEN parsed_budget IS NULL THEN 1 ELSE 0 END) AS unknown_budget,
                   SUM(CASE WHEN parsed_budget IS NOT NULL THEN 1 ELSE 0 END) AS known_budget
                   FROM orders
                   GROUP BY status
                   ORDER BY status;
                   """)
    rows = cursor.fetchall()
    connection.close()

    stats = []
    for row in rows:
        status, total, unknown_budget, known_budget = row
        stats.append({
            "status": status,
            "total": total,
            "unknown_budget": unknown_budget,
            "known_budget": known_budget,
        })
    return stats


def print_budget_quality_stats():
    stats = get_budget_quality_stats()
    print("Качество бюджетов:")
    for item in stats:
        print(item["status"], "total:", item["total"], "unknown:", item["unknown_budget"], "known:", item["known_budget"])


def get_budget_stats():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT status,
                   COUNT(parsed_budget) AS with_budget,
                   MIN(parsed_budget) AS min_budget,
                   MAX(parsed_budget) AS max_budget,
                   ROUND(AVG(parsed_budget), 2) AS avg_budget
                   FROM orders
                   GROUP BY status
                   ORDER BY status;
                   """)
    rows = cursor.fetchall()
    connection.close()

    stats = []
    for row in rows:
        status, with_budget, min_budget, max_budget, avg_budget = row
        stats.append({
            "status": status,
            "with_budget": with_budget,
            "min_budget": min_budget,
            "max_budget": max_budget,
            "avg_budget": avg_budget,
        })
    return stats


def print_budget_stats():
    stats = get_budget_stats()
    print("Бюджеты по статусам:")
    for item in stats:
        print(item["status"], "with_budget:", item["with_budget"], "минимальный бюджет:", item["min_budget"], "максимальный бюджет:", item["max_budget"], "средний бюджет:", item["avg_budget"])


def print_telegram_stats():
    orders = get_unsent_telegram_orders()
    print("Telegram:")
    print("Неотправленных matched/risky:", len(orders))


def get_all_orders(status=None, limit=20):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    if status is None:
        cursor.execute("""
        SELECT id, source, external_id, title, url, budget, status, reason, project_type, parsed_budget, matched_keyword, negative_keyword, risky_keyword, sent_to_telegram, contacted, created_at
        FROM orders
        ORDER BY id DESC
        LIMIT ?
        """, (limit,))
    else:
        cursor.execute("""
        SELECT id, source, external_id, title, url, budget, status, reason, project_type, parsed_budget, matched_keyword, negative_keyword, risky_keyword, sent_to_telegram, contacted, created_at
        FROM orders
        WHERE status = ?
        ORDER BY id DESC
        LIMIT ?
        """, (status, limit))

    rows = cursor.fetchall()
    connection.close()

    orders = []

    for row in rows:
        order = {
            "order_id": row[0],
            "source": row[1],
            "external_id": row[2],
            "title": row[3],
            "url": row[4],
            "budget": row[5],
            "status": row[6],
            "reason": row[7],
            "project_type": row[8],
            "parsed_budget": row[9],
            "matched_keyword": row[10],
            "negative_keyword": row[11],
            "risky_keyword": row[12],
            "sent_to_telegram": row[13],
            "contacted": row[14],
            "created_at": row[15],
        }

        orders.append(order)

    return orders


def get_order_by_source_and_external_id(source, external_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
                SELECT id, source, external_id, title, url, budget, status, reason, project_type, parsed_budget, matched_keyword, negative_keyword, risky_keyword, sent_to_telegram, contacted, created_at
                FROM orders
                WHERE source = ? AND external_id = ?
                LIMIT 1
                """, (source, external_id))
    row = cursor.fetchone()
    connection.close()
    if row is None:
        return None
    order = {
                "order_id": row[0],
                "source": row[1],
                "external_id": row[2],
                "title": row[3],
                "url": row[4],
                "budget": row[5],
                "status": row[6],
                "reason": row[7],
                "project_type": row[8],
                "parsed_budget": row[9],
                "matched_keyword": row[10],
                "negative_keyword": row[11],
                "risky_keyword": row[12],
                "sent_to_telegram": row[13],
                "contacted": row[14],
                "created_at": row[15],
                }

    return order


def print_saved_orders(limit=20):
    orders = get_all_orders(limit=limit)
    print("Сохранённые заказы:")
    for order in orders:
        print(
            order["source"],
            order["external_id"],
            order["order_id"],
            order["title"],
            order["status"],
            order["reason"],
            "type:", order["project_type"],
            "budget:", order["parsed_budget"],
            "match:", order["matched_keyword"],
            "minus:", order["negative_keyword"],
            "tg:", order["sent_to_telegram"],
            "risky_keyword", order["risky_keyword"],
        )


def mark_order_sent_to_telegram(source, external_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE orders
        SET sent_to_telegram = 1
        WHERE source = ? AND external_id = ?
        """, (source, external_id)
    )
    updated_rows = cursor.rowcount

    connection.commit()
    connection.close()

    return updated_rows > 0


def get_unsent_telegram_orders():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
            SELECT source, external_id, title, url, description, budget, status, reason, parsed_budget, matched_keyword, negative_keyword, risky_keyword
            FROM orders
            WHERE status IN ('matched', 'risky') AND sent_to_telegram = 0
            ORDER by id
            """)
    rows = cursor.fetchall()
    connection.close()

    orders = []
    for row in rows:
        order = {
            "source": row[0],
            "external_id": row[1],
            "title": row[2],
            "url": row[3],
            "description": row[4],
            "budget": row[5],
            "status": row[6],
            "reason": row[7],
            "parsed_budget": row[8],
            "matched_keyword": row[9],
            "negative_keyword": row[10],
            "risky_keyword": row[11],
        }
        orders.append(order)
    return orders


def print_unsent_telegram_orders():
    orders = get_unsent_telegram_orders()
    print("Неотправленных в Telegram:", len(orders))

    if len(orders) == 0:
        return
    print("Список неотправленных заказов:")
    for order in orders:
        print(
            order["source"],
            order["external_id"],
            order["title"],
            order["status"],
            "match:", order["matched_keyword"],
            "risky:", order["risky_keyword"],
        )


def update_order_contacted(source, external_id, contacted):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    if contacted:
        contacted_value = 1
    else:
        contacted_value = 0

    cursor.execute("""
        UPDATE orders
        SET contacted = ?
        WHERE source = ? AND external_id = ?
        """, (contacted_value, source, external_id))
    updated_rows = cursor.rowcount
    connection.commit()
    connection.close()

    return updated_rows > 0


if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "default"

    if mode == "count":
        print("Заказов в базе:", get_orders_count())
    elif mode == "recent":
        print_saved_orders(limit=20)
    elif mode == "unsent":
        print_unsent_telegram_orders()
    elif mode == "stats":
        print("Заказов в базе:", get_orders_count())
        print_status_stats()
        print_rejected_reason_stats()
        print_budget_quality_stats()
        print_budget_stats()
        print_telegram_stats()
    else:
        print("Заказов в базе:", get_orders_count())
        print_saved_orders(limit=20)
        print_unsent_telegram_orders()
