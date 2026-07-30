import sqlite3

conn = sqlite3.connect("inventory.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    category TEXT,
    quantity INTEGER,
    price REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully")