import sqlite3

# имя файла, в котором будет лежать наша база данных
DB_NAME = "diary.db"


def get_connection():
    # открываем соединение с базой данных
    connection = sqlite3.connect(DB_NAME)
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # таблица категорий (например: Еда, Зарплата, Транспорт)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT
        )
    """)

    # таблица операций (доходы и расходы)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT,
            type TEXT NOT NULL,
            category_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    """)

    connection.commit()
    connection.close()
    print("Таблицы созданы!")


def add_category(name, category_type, description):
    # добавляем одну категорию в таблицу categories
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO categories (name, type, description) VALUES (?, ?, ?)",
        (name, category_type, description)
    )
    connection.commit()
    connection.close()


def get_categories():
    # достаём все категории из базы
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, type, description FROM categories")
    categories = cursor.fetchall()
    connection.close()
    return categories


def get_category_by_name(name):
    # ищем одну категорию по её названию (нужно, чтобы узнать её id)
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, type, description FROM categories WHERE name = ?", (name,))
    category = cursor.fetchone()
    connection.close()
    return category


def get_fallback_category(transaction_type):
    # запасная категория для операций, которым не нашлась точная.
    # "доход"  -> категория "Прочий доход"
    # "расход" -> категория "Прочий расход"
    if transaction_type == "доход":
        return get_category_by_name("Прочий доход")
    else:
        return get_category_by_name("Прочий расход")


def add_transaction(amount, description, transaction_type, category_id):
    # сохраняем одну операцию в таблицу transactions
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO transactions (amount, description, type, category_id) VALUES (?, ?, ?, ?)",
        (amount, description, transaction_type, category_id)
    )
    connection.commit()
    connection.close()


def get_transactions():
    # достаём все операции из базы, вместе с названием категории.
    # JOIN соединяет таблицу операций с таблицей категорий по category_id.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            transactions.id,
            transactions.amount,
            transactions.description,
            transactions.type,
            categories.name,
            transactions.created_at
        FROM transactions
        LEFT JOIN categories ON transactions.category_id = categories.id
        ORDER BY transactions.id DESC
    """)
    transactions = cursor.fetchall()
    connection.close()
    return transactions


# этот блок выполняется, только если запустить файл напрямую: python database.py
if __name__ == "__main__":
    create_tables()