import sqlite3

DB_NAME = "diary.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subcategories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            UNIQUE (category_id, name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            quantity REAL,
            unit TEXT,
            comment TEXT,
            type TEXT NOT NULL,
            object_id INTEGER,
            category_id INTEGER,
            subcategory_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (object_id) REFERENCES objects (id),
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (subcategory_id) REFERENCES subcategories (id)
        )
    """)

    connection.commit()
    connection.close()
    print("Таблицы созданы")


def add_object(name, description=""):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO objects (name, description) VALUES (?, ?)", (name, description))
    connection.commit()
    connection.close()


def get_objects():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, description FROM objects")
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_object_by_name(name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, description FROM objects WHERE name = ?", (name,))
    row = cursor.fetchone()
    connection.close()
    return row


def add_category(name, category_type, description=""):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO categories (name, type, description) VALUES (?, ?, ?)",
                   (name, category_type, description))
    connection.commit()
    connection.close()


def get_categories():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, type, description FROM categories")
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_category_by_name(name):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, type, description FROM categories WHERE name = ?", (name,))
    row = cursor.fetchone()
    connection.close()
    return row


def add_subcategory(name, category_id, description=""):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO subcategories (name, category_id, description) VALUES (?, ?, ?)",
                   (name, category_id, description))
    connection.commit()
    connection.close()


def get_subcategories(category_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, category_id, description FROM subcategories WHERE category_id = ?", (category_id,))
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_subcategory_by_name(name, category_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, category_id, description FROM subcategories WHERE name = ? AND category_id = ?",
                   (name, category_id))
    row = cursor.fetchone()
    connection.close()
    return row


def add_transaction(amount, comment, transaction_type, object_id, category_id, subcategory_id, quantity=None, unit=None):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO transactions (amount, quantity, unit, comment, type, object_id, category_id, subcategory_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (amount, quantity, unit, comment, transaction_type, object_id, category_id, subcategory_id))
    connection.commit()
    connection.close()


def get_transactions():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT
            transactions.id,
            transactions.amount,
            transactions.quantity,
            transactions.unit,
            transactions.comment,
            transactions.type,
            objects.name,
            categories.name,
            subcategories.name,
            transactions.created_at
        FROM transactions
        LEFT JOIN objects ON transactions.object_id = objects.id
        LEFT JOIN categories ON transactions.category_id = categories.id
        LEFT JOIN subcategories ON transactions.subcategory_id = subcategories.id
        ORDER BY transactions.id DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


if __name__ == "__main__":
    create_tables()
