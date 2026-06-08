import sqlite3


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

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")