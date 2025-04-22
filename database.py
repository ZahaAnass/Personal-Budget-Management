import sqlite3

def create_tables():
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL 
        )
    ''')   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            UNIQUE(category, month)
        )
    ''')
    conn.commit()
    conn.close()
    initialize_categories()

def initialize_categories():
    default_categories = [
        ("Food", "expense"),
        ("Transport", "expense"),
        ("Entertainment", "expense"),
        ("Utilities", "expense"),
        ("Salary", "income"),
        ("Freelance", "income")
    ]
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    for category in default_categories:
        try:
            cursor.execute('INSERT INTO categories (name, type) VALUES (?, ?)', category)
        except sqlite3.IntegrityError:
            pass  # Category already exists
    conn.commit()
    conn.close()

def add_transaction(date, type, category, amount, description=""):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, type, category, amount, description))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def update_transaction(id_, date, type, category, amount, description):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE transactions 
        SET date=?, type=?, category=?, amount=?, description=?
        WHERE id=?
    ''', (date, type, category, amount, description, id_))
    conn.commit()
    conn.close()

def delete_transaction(id_):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id=?', (id_,))
    conn.commit()
    conn.close()

def get_categories(type=None):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    if type:
        cursor.execute('SELECT name FROM categories WHERE type=?', (type,))
    else:
        cursor.execute('SELECT name FROM categories')
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories

def set_budget(category, amount, month):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (category, amount, month)
        VALUES (?, ?, ?)
    ''', (category, amount, month))
    conn.commit()
    conn.close()

def get_budget(category, month):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('SELECT amount FROM budgets WHERE category=? AND month=?', (category, month))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_monthly_totals(month):
    conn = sqlite3.connect('budget.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, SUM(amount) 
        FROM transactions 
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY category
    ''', (month,))
    results = dict(cursor.fetchall())
    conn.close()
    return results