import sqlite3


# ==========================================
# CONNECT TO DATABASE
# ==========================================

conn = sqlite3.connect("inventory.db")

cursor = conn.cursor()


# Enable foreign key support
cursor.execute("PRAGMA foreign_keys = ON")


# ==========================================
# PRODUCTS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
""")


# ==========================================
# CUSTOMERS TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    phone TEXT
)
""")


# ==========================================
# SALES TABLE
# ==========================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    total REAL NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id),

    FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
)
""")


# ==========================================
# SAVE CHANGES
# ==========================================

conn.commit()


# ==========================================
# CLOSE DATABASE
# ==========================================

conn.close()


print("======================================")
print("   DATABASE CREATED SUCCESSFULLY!")
print("======================================")
print(" Products table created")
print(" Customers table created")
print(" Sales table created")
print(" Foreign keys enabled")
print("======================================")