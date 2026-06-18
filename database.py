import sqlite3

DB_NAME = "diary.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT
        )
    """)

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
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, type, description FROM categories")
    categories = cursor.fetchall()
    connection.close()
    return categories


if __name__ == "__main__":
    create_tables()