from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "inventory_secret_key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def connect_db():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def init_db():

    conn = connect_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT
        )
    """)

    # -----------------------------------------------------
    # SALES
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # ADD customer_id TO OLD SALES TABLE IF REQUIRED
    # -----------------------------------------------------

    cursor.execute("PRAGMA table_info(sales)")

    columns = [column["name"] for column in cursor.fetchall()]

    if "customer_id" not in columns:

        cursor.execute("""
            ALTER TABLE sales
            ADD COLUMN customer_id INTEGER
        """)

    conn.commit()
    conn.close()


# =========================================================
# DASHBOARD / HOME
# =========================================================

@app.route("/")
def home():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY product_id DESC
    """)

    products = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
    """)

    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT category)
        FROM products
    """)

    total_categories = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE quantity < 10
    """)

    low_stock = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(quantity * price)
        FROM products
    """)

    total_value = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value,
        total_sales=total_sales,
        total_revenue=total_revenue
    )


# =========================================================
# ADD PRODUCT
# =========================================================

@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]

        try:

            quantity = int(request.form["quantity"])
            price = float(request.form["price"])

            if quantity < 0 or price < 0:

                flash(
                    "Quantity and price cannot be negative.",
                    "danger"
                )

                return redirect("/add")

        except ValueError:

            flash(
                "Please enter valid quantity and price.",
                "danger"
            )

            return redirect("/add")

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO products
            (product_name, category, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            category,
            quantity,
            price
        ))

        conn.commit()
        conn.close()

        flash(
            "Product added successfully!",
            "success"
        )

        return redirect("/")

    return render_template("add_product.html")


# =========================================================
# SEARCH PRODUCT
# =========================================================

@app.route("/search")
def search():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM products
        WHERE product_name LIKE ?
        OR category LIKE ?
        ORDER BY product_id DESC
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    products = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
    """)

    total_products = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(DISTINCT category)
        FROM products
    """)

    total_categories = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE quantity < 10
    """)

    low_stock = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(quantity * price)
        FROM products
    """)

    total_value = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value,
        total_sales=total_sales,
        total_revenue=total_revenue
    )


# =========================================================
# EDIT PRODUCT
# =========================================================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]

        try:

            quantity = int(request.form["quantity"])
            price = float(request.form["price"])

            if quantity < 0 or price < 0:

                flash(
                    "Quantity and price cannot be negative.",
                    "danger"
                )

                conn.close()

                return redirect(
                    f"/edit/{id}"
                )

        except ValueError:

            flash(
                "Please enter valid quantity and price.",
                "danger"
            )

            conn.close()

            return redirect(
                f"/edit/{id}"
            )

        cursor.execute("""
            UPDATE products
            SET product_name = ?,
                category = ?,
                quantity = ?,
                price = ?
            WHERE product_id = ?
        """, (
            name,
            category,
            quantity,
            price,
            id
        ))

        conn.commit()
        conn.close()

        flash(
            "Product updated successfully!",
            "success"
        )

        return redirect("/")

    cursor.execute("""
        SELECT *
        FROM products
        WHERE product_id = ?
    """, (id,))

    product = cursor.fetchone()

    conn.close()

    if product is None:

        flash(
            "Product not found.",
            "danger"
        )

        return redirect("/")

    return render_template(
        "edit_product.html",
        product=product
    )


# =========================================================
# DELETE PRODUCT
# =========================================================

@app.route("/delete/<int:id>")
def delete(id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
        WHERE product_id = ?
    """, (id,))

    sales_count = cursor.fetchone()[0]

    if sales_count > 0:

        conn.close()

        flash(
            "This product cannot be deleted because it has sales records.",
            "danger"
        )

        return redirect("/")

    cursor.execute("""
        DELETE FROM products
        WHERE product_id = ?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Product deleted successfully!",
        "success"
    )

    return redirect("/")


# =========================================================
# CUSTOMER LIST
# =========================================================

@app.route("/customers")
def customers():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """)

    customers = cursor.fetchall()

    conn.close()

    return render_template(
        "customer.html",
        customers=customers
    )


# =========================================================
# ADD CUSTOMER
# =========================================================

@app.route("/add-customer", methods=["POST"])
def add_customer():

    name = request.form["customer_name"]
    phone = request.form["phone"]

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO customers
        (customer_name, phone)
        VALUES (?, ?)
    """, (
        name,
        phone
    ))

    conn.commit()
    conn.close()

    flash(
        "Customer added successfully!",
        "success"
    )

    return redirect("/customers")


# =========================================================
# NEW SALE
# =========================================================

@app.route("/new-sale", methods=["GET", "POST"])
def new_sale():

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":

        try:

            product_id = int(
                request.form["product_id"]
            )

            customer_id = int(
                request.form["customer_id"]
            )

            quantity = int(
                request.form["quantity"]
            )

        except ValueError:

            conn.close()

            flash(
                "Please enter valid values.",
                "danger"
            )

            return redirect("/new-sale")

        if quantity <= 0:

            conn.close()

            flash(
                "Sale quantity must be greater than zero.",
                "danger"
            )

            return redirect("/new-sale")

        # -------------------------------------------------
        # PRODUCT
        # -------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM products
            WHERE product_id = ?
        """, (product_id,))

        product = cursor.fetchone()

        if product is None:

            conn.close()

            flash(
                "Product not found.",
                "danger"
            )

            return redirect("/new-sale")

        # -------------------------------------------------
        # CUSTOMER
        # -------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,))

        customer = cursor.fetchone()

        if customer is None:

            conn.close()

            flash(
                "Customer not found.",
                "danger"
            )

            return redirect("/new-sale")

        # -------------------------------------------------
        # STOCK CHECK
        # -------------------------------------------------

        if quantity > product["quantity"]:

            conn.close()

            flash(
                f"Only {product['quantity']} units available.",
                "danger"
            )

            return redirect("/new-sale")

        # -------------------------------------------------
        # CALCULATE SALE
        # -------------------------------------------------

        price = product["price"]

        total = quantity * price

        # -------------------------------------------------
        # INSERT SALE
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO sales
            (
                product_id,
                customer_id,
                quantity,
                price,
                total
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            customer_id,
            quantity,
            price,
            total
        ))

        sale_id = cursor.lastrowid

        # -------------------------------------------------
        # REDUCE INVENTORY
        # -------------------------------------------------

        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (
            quantity,
            product_id
        ))

        conn.commit()

        conn.close()

        flash(
            "Sale completed successfully!",
            "success"
        )

        # DIRECTLY OPEN INVOICE
        return redirect(
            f"/invoice/{sale_id}"
        )

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM products
        WHERE quantity > 0
        ORDER BY product_name
    """)

    products = cursor.fetchall()

    # -----------------------------------------------------
    # CUSTOMERS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_name
    """)

    customers = cursor.fetchall()

    conn.close()

    return render_template(
        "new_sale.html",
        products=products,
        customers=customers
    )


# =========================================================
# SALES HISTORY
# =========================================================

@app.route("/sales")
def sales():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.sale_id,
            products.product_name,
            products.category,
            customers.customer_name,
            customers.phone,
            sales.quantity,
            sales.price,
            sales.total,
            sales.sale_date

        FROM sales

        JOIN products
        ON sales.product_id = products.product_id

        LEFT JOIN customers
        ON sales.customer_id = customers.customer_id

        ORDER BY sales.sale_id DESC
    """)

    sales_data = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "sales.html",
        sales=sales_data,
        total_revenue=total_revenue,
        total_sales=total_sales
    )


# =========================================================
# SEARCH SALES
# =========================================================

@app.route("/search-sales")
def search_sales():

    keyword = request.args.get(
        "keyword",
        ""
    ).strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sales.sale_id,
            products.product_name,
            products.category,
            customers.customer_name,
            customers.phone,
            sales.quantity,
            sales.price,
            sales.total,
            sales.sale_date

        FROM sales

        JOIN products
        ON sales.product_id = products.product_id

        LEFT JOIN customers
        ON sales.customer_id = customers.customer_id

        WHERE products.product_name LIKE ?
        OR products.category LIKE ?
        OR customers.customer_name LIKE ?

        ORDER BY sales.sale_id DESC
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    sales_data = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM sales
    """)

    total_sales = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "sales.html",
        sales=sales_data,
        total_revenue=total_revenue,
        total_sales=total_sales
    )


# =========================================================
# INVOICE
# =========================================================

@app.route("/invoice/<int:sale_id>")
def invoice(sale_id):

    conn = connect_db()
    cursor = conn.cursor()

    # -----------------------------------------------------
    # GET SALE + PRODUCT + CUSTOMER
    # -----------------------------------------------------

    cursor.execute("""
        SELECT
            sales.sale_id,
            sales.quantity,
            sales.price,
            sales.total,
            sales.sale_date,

            products.product_name,
            products.category,

            customers.customer_name,
            customers.phone

        FROM sales

        JOIN products
        ON sales.product_id = products.product_id

        LEFT JOIN customers
        ON sales.customer_id = customers.customer_id

        WHERE sales.sale_id = ?
    """, (sale_id,))

    sale = cursor.fetchone()

    conn.close()

    if sale is None:

        flash(
            "Invoice not found.",
            "danger"
        )

        return redirect("/sales")

    # -----------------------------------------------------
    # INVOICE CALCULATION
    # -----------------------------------------------------

    subtotal = sale["total"]

    # You can change these values
    discount = 0

    gst_rate = 18

    taxable_amount = subtotal - discount

    gst = taxable_amount * gst_rate / 100

    grand_total = taxable_amount + gst

    # -----------------------------------------------------
    # INVOICE NUMBER
    # -----------------------------------------------------

    invoice_no = f"INV-{sale_id:05d}"

    return render_template(
        "invoice.html",

        sale=sale,

        invoice_no=invoice_no,

        subtotal=subtotal,

        discount=discount,

        gst_rate=gst_rate,

        gst=gst,

        grand_total=grand_total
    )


# =========================================================
# DELETE SALE
# =========================================================

@app.route("/delete-sale/<int:id>")
def delete_sale(id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM sales
        WHERE sale_id = ?
    """, (id,))

    sale = cursor.fetchone()

    if sale is None:

        conn.close()

        flash(
            "Sale not found.",
            "danger"
        )

        return redirect("/sales")

    # Restore stock

    cursor.execute("""
        UPDATE products
        SET quantity = quantity + ?
        WHERE product_id = ?
    """, (
        sale["quantity"],
        sale["product_id"]
    ))

    # Delete sale

    cursor.execute("""
        DELETE FROM sales
        WHERE sale_id = ?
    """, (id,))

    conn.commit()
    conn.close()

    flash(
        "Sale deleted and stock restored successfully!",
        "success"
    )

    return redirect("/sales")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)