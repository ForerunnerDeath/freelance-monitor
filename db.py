import sqlite3
from datetime import datetime


DB_NAME = "freelance_monitor.db"


def init_db():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            title TEXT,
            budget TEXT,
            status TEXT,
            reason TEXT,
            created_at TEXT
        )
    """)

    connection.commit()
    connection.close()

def is_order_seen(order_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT 1 FROM orders WHERE order_id = ? LIMIT 1",
        (order_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return False
    else:
        return True

def save_order(order, status, reason):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    order_id = order.get("id")
    title = order.get("title", "Без названия")

    raw_budget = order.get("budget")
    if raw_budget is None:
        budget = ""
    else:
        budget = str(raw_budget)

    created_at = datetime.now().isoformat(timespec="seconds")

    cursor.execute(
        """
        INSERT INTO orders (
            order_id,
            title,
            budget,
            status,
            reason,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (order_id, title, budget, status, reason, created_at)
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


def get_all_orders():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
    SELECT order_id, title, budget, status, reason, created_at
    FROM orders
    ORDER BY id
    """)

    rows = cursor.fetchall()
    connection.close()

    orders = []

    for row in rows:
        order = {
            "order_id": row[0],
            "title": row[1],
            "budget": row[2],
            "status": row[3],
            "reason": row[4],
            "created_at": row[5],
        }

        orders.append(order)

    return orders

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")
    print("Заказов в базе:", get_orders_count())
    orders = get_all_orders()

    print("Сохранённые заказы:")

    for order in orders:
        print(order["order_id"], order["title"], order["status"], order["reason"])