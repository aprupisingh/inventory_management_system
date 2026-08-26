from flask import Flask, Response, render_template, request, redirect, flash
import csv
from datetime import datetime
import io
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

app = Flask(__name__, static_folder="statics", static_url_path="/static")
app.secret_key = "inventory_secret_key"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def connect_db():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_sales_chart():

    conn = connect_db()
    category_sales = conn.execute("""
        SELECT products.category, SUM(sales.quantity) AS quantity_sold
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        GROUP BY products.category
        ORDER BY quantity_sold DESC
    """).fetchall()
    conn.close()

    chart_path = os.path.join(
        app.static_folder,
        "sales_by_category.png"
    )

    categories = [row["category"] for row in category_sales]
    quantities = [row["quantity_sold"] for row in category_sales]

    plt.figure(figsize=(9, 4.5))

    if category_sales:

        plt.pie(
            quantities,
            labels=categories,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Set3.colors[:len(categories)]
        )
        plt.title("Sales by Product Category")
        plt.legend(
            categories,
            title="Product Types",
            loc="center left",
            bbox_to_anchor=(1, 0.5)
        )
        plt.axis("equal")

    else:

        plt.text(
            0.5,
            0.5,
            "No sales recorded yet",
            ha="center",
            va="center",
            fontsize=14
        )
        plt.title("Sales by Product Category")
        plt.xticks([])
        plt.yticks([])

    plt.tight_layout()
    plt.savefig(chart_path, dpi=120)
    plt.close()

    return "sales_by_category.png"


def create_reports_chart(daily_sales, category_sales, payment_sales):

    chart_path = os.path.join(app.static_folder, "reports_analytics.png")
    figure, axes = plt.subplots(1, 3, figsize=(16, 4.5))

    if daily_sales:

        daily_frame = pd.DataFrame(daily_sales)
        axes[0].plot(
            daily_frame["sale_date"],
            daily_frame["revenue"],
            marker="o",
            color="#0d6efd"
        )
        axes[0].set_title("Daily Sales Trend")
        axes[0].tick_params(axis="x", rotation=35)
        axes[0].set_ylabel("Revenue")

    else:

        axes[0].text(0.5, 0.5, "No sales data", ha="center", va="center")
        axes[0].set_title("Daily Sales Trend")

    if category_sales:

        category_frame = pd.DataFrame(category_sales)
        axes[1].bar(
            category_frame["category"],
            category_frame["units_sold"],
            color="#198754"
        )
        axes[1].set_title("Category-wise Sales")
        axes[1].tick_params(axis="x", rotation=35)
        axes[1].set_ylabel("Units")

    else:

        axes[1].text(0.5, 0.5, "No sales data", ha="center", va="center")
        axes[1].set_title("Category-wise Sales")

    if payment_sales:

        payment_frame = pd.DataFrame(payment_sales)
        axes[2].pie(
            payment_frame["revenue"],
            labels=payment_frame["payment_method"],
            autopct="%1.1f%%"
        )
        axes[2].set_title("Revenue by Payment Method")

    else:

        axes[2].text(0.5, 0.5, "No payment data", ha="center", va="center")
        axes[2].set_title("Revenue by Payment Method")

    figure.tight_layout()
    figure.savefig(chart_path, dpi=120)
    plt.close(figure)

    return "reports_analytics.png"


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
            discount REAL NOT NULL DEFAULT 0,
            gst_rate REAL NOT NULL DEFAULT 18,
            gst REAL NOT NULL DEFAULT 0,
            grand_total REAL NOT NULL DEFAULT 0,
            payment_method TEXT NOT NULL DEFAULT 'Cash',
            payment_amount REAL NOT NULL DEFAULT 0,
            payment_status TEXT NOT NULL DEFAULT 'Paid',
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            transaction_id TEXT,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (product_id)
            REFERENCES products(product_id),

            FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            return_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            refund_amount REAL NOT NULL,
            reason TEXT NOT NULL,
            return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
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

    sales_columns = [column["name"] for column in cursor.execute(
        "PRAGMA table_info(sales)"
    ).fetchall()]

    for column_name, column_definition in [
        ("discount", "REAL NOT NULL DEFAULT 0"),
        ("gst_rate", "REAL NOT NULL DEFAULT 18"),
        ("gst", "REAL NOT NULL DEFAULT 0"),
        ("grand_total", "REAL NOT NULL DEFAULT 0"),
        ("payment_method", "TEXT NOT NULL DEFAULT 'Cash'"),
        ("payment_amount", "REAL NOT NULL DEFAULT 0"),
        ("payment_status", "TEXT NOT NULL DEFAULT 'Paid'"),
        ("payment_date", "TIMESTAMP"),
        ("transaction_id", "TEXT")
    ]:

        if column_name not in sales_columns:

            cursor.execute(
                f"ALTER TABLE sales ADD COLUMN {column_name} {column_definition}"
            )

    cursor.execute("""
        UPDATE sales
        SET gst = (total - discount) * gst_rate / 100,
            grand_total = (total - discount) + ((total - discount) * gst_rate / 100),
            payment_amount = CASE WHEN payment_amount = 0 THEN
                (total - discount) + ((total - discount) * gst_rate / 100)
                ELSE payment_amount END,
            payment_date = COALESCE(payment_date, sale_date)
        WHERE grand_total = 0
    """)

    cursor.execute("""
        UPDATE sales
        SET payment_amount = grand_total,
            payment_date = COALESCE(payment_date, sale_date)
        WHERE payment_amount = 0
    """)

    customer_list = [
        ("Rahul Sharma", "9876543210"),
        ("Priya Patel", "9123456789"),
        ("Amit Verma", "9988776655"),
        ("Neha Singh", "9012345678"),
        ("Rohit Kumar", "9345678901"),
        ("Anjali Mehta", "9765432109"),
        ("Arjun Shah", "8899776655"),
        ("Pooja Joshi", "9098765432"),
        ("Vivek Gupta", "9876012345"),
        ("Sneha Desai", "8765432109")
    ]

    cursor.execute("""
        DELETE FROM customers
        WHERE customer_name LIKE 'Sample Customer %'
    """)

    if cursor.rowcount > 0 or cursor.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0] == 0:

        cursor.executemany("""
            INSERT INTO customers
            (customer_name, phone)
            VALUES (?, ?)
        """, customer_list)

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
        SELECT SUM(grand_total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    sales_chart = create_sales_chart()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value,
        total_sales=total_sales,
        total_revenue=total_revenue,
        sales_chart=sales_chart
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

        except (KeyError, ValueError):

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
# IMPORT PRODUCTS FROM CSV
# =========================================================

@app.route("/import-products", methods=["POST"])
def import_products():

    uploaded_file = request.files.get("product_file")

    if uploaded_file is None or uploaded_file.filename == "":

        flash(
            "Please select a CSV file to import.",
            "danger"
        )

        return redirect("/add")

    try:

        file_text = uploaded_file.stream.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(file_text))
        required_columns = {
            "product name",
            "category",
            "quantity",
            "price"
        }

        if reader.fieldnames is None:

            raise ValueError("The CSV file is empty.")

        column_map = {
            column.strip().lower(): column
            for column in reader.fieldnames
            if column is not None
        }

        if not required_columns.issubset(column_map):

            raise ValueError(
                "CSV must contain Product Name, Category, Quantity, and Price columns."
            )

        products = []

        for row_number, row in enumerate(reader, start=2):

            name = row.get(column_map["product name"], "").strip()
            category = row.get(column_map["category"], "").strip()

            if not name or not category:

                raise ValueError(
                    f"Row {row_number}: product name and category are required."
                )

            quantity = int(row.get(column_map["quantity"], "").strip())
            price = float(row.get(column_map["price"], "").strip())

            if quantity < 0 or price < 0:

                raise ValueError(
                    f"Row {row_number}: quantity and price cannot be negative."
                )

            products.append((name, category, quantity, price))

        if not products:

            raise ValueError("The CSV file contains no products.")

        conn = connect_db()

        conn.executemany("""
            INSERT INTO products
            (product_name, category, quantity, price)
            VALUES (?, ?, ?, ?)
        """, products)

        conn.commit()
        conn.close()

    except (UnicodeDecodeError, ValueError, TypeError):

        flash(
            "CSV import failed. Check the file format and values.",
            "danger"
        )

        return redirect("/add")

    flash(
        f"{len(products)} products imported successfully!",
        "success"
    )

    return redirect("/")


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
        SELECT SUM(grand_total)
        FROM sales
    """)

    total_revenue = cursor.fetchone()[0] or 0

    conn.close()

    sales_chart = create_sales_chart()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value,
        total_sales=total_sales,
        total_revenue=total_revenue,
        sales_chart=sales_chart
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

        try:

            discount = float(request.form.get("discount", 0))
            gst_rate = float(request.form.get("gst_rate", 18))
            payment_amount = float(request.form.get("payment_amount", 0))

        except ValueError:

            conn.close()
            flash("Please enter valid discount and GST values.", "danger")
            return redirect("/new-sale")

        payment_method = request.form.get("payment_method", "Cash")
        payment_status = request.form.get("payment_status", "Paid")
        transaction_id = request.form.get("transaction_id", "").strip()
        payment_date = request.form.get("payment_date") or datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        payment_methods = {
            "Cash",
            "UPI",
            "Credit Card",
            "Debit Card",
            "Net Banking"
        }
        payment_statuses = {"Paid", "Pending", "Partially Paid"}

        if payment_method not in payment_methods or payment_status not in payment_statuses:

            conn.close()
            flash("Please select a valid payment method and status.", "danger")
            return redirect("/new-sale")

        if quantity <= 0:

            conn.close()

            flash(
                "Sale quantity must be greater than zero.",
                "danger"
            )

            return redirect("/new-sale")

        if discount < 0 or gst_rate < 0:

            conn.close()
            flash("Discount and GST rate cannot be negative.", "danger")
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
        if discount > total:

            conn.close()
            flash("Discount cannot be greater than the sale subtotal.", "danger")
            return redirect("/new-sale")

        taxable_amount = total - discount
        gst = taxable_amount * gst_rate / 100
        grand_total = taxable_amount + gst

        if payment_amount < 0 or payment_amount > grand_total:

            conn.close()
            flash("Payment amount must be between 0 and the final amount.", "danger")
            return redirect("/new-sale")

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
                total,
                discount,
                gst_rate,
                gst,
                grand_total,
                payment_method,
                payment_amount,
                payment_status,
                payment_date,
                transaction_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_id,
            customer_id,
            quantity,
            price,
            total,
            discount,
            gst_rate,
            gst,
            grand_total,
            payment_method,
            payment_amount,
            payment_status,
            payment_date,
            transaction_id
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
            sales.discount,
            sales.gst_rate,
            sales.gst,
            sales.grand_total,
            sales.payment_method,
            sales.payment_amount,
            sales.payment_status,
            sales.payment_date,
            sales.transaction_id,
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
        SELECT SUM(grand_total)
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
            sales.discount,
            sales.gst_rate,
            sales.gst,
            sales.grand_total,
            sales.payment_method,
            sales.payment_amount,
            sales.payment_status,
            sales.payment_date,
            sales.transaction_id,
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
        SELECT SUM(grand_total)
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
# EXPORT SALES HISTORY
# =========================================================

@app.route("/export-sales")
def export_sales():

    keyword = request.args.get("keyword", "").strip()
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT
            sales.sale_id,
            products.product_name,
            products.category,
            customers.customer_name,
            customers.phone,
            sales.quantity,
            sales.price,
            sales.total,
            sales.discount,
            sales.gst_rate,
            sales.gst,
            sales.grand_total,
            sales.payment_method,
            sales.payment_amount,
            sales.payment_status,
            sales.payment_date,
            sales.transaction_id,
            sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
    """

    params = []

    if keyword:

        query += """
            WHERE products.product_name LIKE ?
            OR products.category LIKE ?
            OR customers.customer_name LIKE ?
        """

        params = ["%" + keyword + "%"] * 3

    query += " ORDER BY sales.sale_id DESC"
    cursor.execute(query, params)
    sales_data = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Sale ID",
        "Product",
        "Category",
        "Customer",
        "Phone",
        "Quantity",
        "Price",
        "Total",
        "Discount",
        "GST Rate",
        "GST",
        "Final Amount",
        "Payment Method",
        "Payment Amount",
        "Payment Status",
        "Payment Date",
        "Transaction ID",
        "Sale Date"
    ])

    for sale in sales_data:

        writer.writerow([
            sale["sale_id"],
            sale["product_name"],
            sale["category"],
            sale["customer_name"] or "Walk-in Customer",
            sale["phone"] or "",
            sale["quantity"],
            sale["price"],
            sale["total"],
            sale["discount"],
            sale["gst_rate"],
            sale["gst"],
            sale["grand_total"],
            sale["payment_method"],
            sale["payment_amount"],
            sale["payment_status"],
            sale["payment_date"],
            sale["transaction_id"] or "",
            sale["sale_date"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=sales_history.csv"
        }
    )


@app.route("/export-sales-pdf")
def export_sales_pdf():

    keyword = request.args.get("keyword", "").strip()
    conn = connect_db()
    query = """
        SELECT
            sales.sale_id, products.product_name, products.category,
            customers.customer_name, sales.quantity, sales.total,
            sales.discount, sales.gst, sales.grand_total,
            sales.payment_method, sales.payment_status, sales.payment_date
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
    """
    params = []

    if keyword:

        query += """
            WHERE products.product_name LIKE ?
            OR products.category LIKE ?
            OR customers.customer_name LIKE ?
        """
        params = ["%" + keyword + "%"] * 3

    query += " ORDER BY sales.sale_id DESC"
    sales_data = conn.execute(query, params).fetchall()
    conn.close()

    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=landscape(letter),
        rightMargin=0.35 * inch,
        leftMargin=0.35 * inch,
        topMargin=0.35 * inch,
        bottomMargin=0.35 * inch
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Sales History Report", styles["Title"]),
        Spacer(1, 0.15 * inch)
    ]
    table_data = [[
        "Sale ID", "Product", "Category", "Customer", "Qty",
        "Subtotal", "Discount", "GST", "Final Amount", "Method",
        "Status", "Payment Date"
    ]]

    for sale in sales_data:

        table_data.append([
            sale["sale_id"],
            sale["product_name"],
            sale["category"],
            sale["customer_name"] or "Walk-in Customer",
            sale["quantity"],
            f"INR {sale['total']:.2f}",
            f"INR {sale['discount']:.2f}",
            f"INR {sale['gst']:.2f}",
            f"INR {sale['grand_total']:.2f}",
            sale["payment_method"],
            sale["payment_status"],
            sale["payment_date"] or ""
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#212529")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")])
    ]))
    elements.append(table)
    document.build(elements)

    return Response(
        output.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=sales_history.pdf"
        }
    )


# =========================================================
# REPORTS AND ANALYTICS
# =========================================================

@app.route("/reports")
def reports():

    conn = connect_db()

    sales_frame = pd.read_sql_query("""
        SELECT
            sales.sale_id,
            sales.quantity,
            sales.total,
            sales.grand_total,
            sales.payment_method,
            sales.sale_date,
            products.product_name,
            products.category,
            products.price,
            customers.customer_name
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
    """, conn)

    returns_frame = pd.read_sql_query("""
        SELECT sale_id, quantity, refund_amount
        FROM returns
    """, conn)

    inventory_frame = pd.read_sql_query("""
        SELECT product_name, category, quantity, price
        FROM products
    """, conn)
    conn.close()

    if returns_frame.empty:

        returns_by_sale = pd.DataFrame(columns=["sale_id", "returned_quantity", "refund_amount"])

    else:

        returns_by_sale = returns_frame.groupby("sale_id", as_index=False).agg(
            returned_quantity=("quantity", "sum"),
            refund_amount=("refund_amount", "sum")
        )

    if sales_frame.empty:

        sales_frame = pd.DataFrame(columns=[
            "sale_id", "quantity", "total", "grand_total", "payment_method",
            "sale_date", "product_name", "category", "price", "customer_name"
        ])
        sales_frame["returned_quantity"] = pd.Series(dtype=float)
        sales_frame["refund_amount"] = pd.Series(dtype=float)

    else:

        sales_frame = sales_frame.merge(returns_by_sale, on="sale_id", how="left")
        sales_frame[["returned_quantity", "refund_amount"]] = sales_frame[
            ["returned_quantity", "refund_amount"]
        ].fillna(0)

    sales_frame["net_quantity"] = sales_frame["quantity"] - sales_frame["returned_quantity"]
    sales_frame["net_revenue"] = sales_frame["grand_total"] - sales_frame["refund_amount"]

    daily_frame = sales_frame.copy()

    if not daily_frame.empty:

        daily_frame["sale_date"] = pd.to_datetime(daily_frame["sale_date"]).dt.strftime("%Y-%m-%d")
        daily_report = daily_frame.groupby("sale_date", as_index=False).agg(
            units_sold=("net_quantity", "sum"),
            revenue=("net_revenue", "sum")
        ).sort_values("sale_date")

    else:

        daily_report = pd.DataFrame(columns=["sale_date", "units_sold", "revenue"])

    monthly_frame = sales_frame.copy()

    if not monthly_frame.empty:

        monthly_frame["month"] = pd.to_datetime(monthly_frame["sale_date"]).dt.strftime("%Y-%m")
        monthly_report = monthly_frame.groupby("month", as_index=False).agg(
            units_sold=("net_quantity", "sum"),
            revenue=("net_revenue", "sum")
        ).sort_values("month")

    else:

        monthly_report = pd.DataFrame(columns=["month", "units_sold", "revenue"])

    top_products = sales_frame.groupby("product_name", as_index=False).agg(
        units_sold=("net_quantity", "sum"),
        revenue=("net_revenue", "sum")
    ).sort_values(["units_sold", "revenue"], ascending=False).head(10)

    top_customers = sales_frame.assign(
        customer_name=sales_frame["customer_name"].fillna("Walk-in Customer")
    ).groupby("customer_name", as_index=False).agg(
        purchases=("sale_id", "count"),
        revenue=("net_revenue", "sum")
    ).sort_values("revenue", ascending=False).head(10)

    category_report = sales_frame.groupby("category", as_index=False).agg(
        units_sold=("net_quantity", "sum"),
        revenue=("net_revenue", "sum")
    ).sort_values("units_sold", ascending=False)

    payment_report = sales_frame.groupby("payment_method", as_index=False).agg(
        revenue=("net_revenue", "sum")
    ).sort_values("revenue", ascending=False)

    inventory_frame["inventory_value"] = inventory_frame["quantity"] * inventory_frame["price"]
    low_stock = inventory_frame[inventory_frame["quantity"] < 10].sort_values("quantity")
    inventory_value = inventory_frame["inventory_value"].sum()
    net_sales_units = sales_frame["net_quantity"].sum()
    estimated_purchases = inventory_frame["quantity"].sum() + net_sales_units
    revenue = sales_frame["net_revenue"].sum()
    returns_total = returns_frame["refund_amount"].sum() if not returns_frame.empty else 0
    profit_loss = None
    chart = create_reports_chart(
        daily_report.to_dict("records"),
        category_report.to_dict("records"),
        payment_report.to_dict("records")
    )

    return render_template(
        "reports.html",
        daily_report=daily_report.to_dict("records"),
        monthly_report=monthly_report.to_dict("records"),
        top_products=top_products.to_dict("records"),
        top_customers=top_customers.to_dict("records"),
        category_report=category_report.to_dict("records"),
        payment_report=payment_report.to_dict("records"),
        low_stock=low_stock.to_dict("records"),
        inventory_value=inventory_value,
        estimated_purchases=estimated_purchases,
        net_sales_units=net_sales_units,
        revenue=revenue,
        returns_total=returns_total,
        profit_loss=profit_loss,
        chart=chart
    )


# =========================================================
# EDIT SALE
# =========================================================

@app.route("/edit-sale/<int:id>", methods=["GET", "POST"])
def edit_sale(id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sales WHERE sale_id = ?", (id,))
    sale = cursor.fetchone()

    if sale is None:

        conn.close()
        flash("Sale not found.", "danger")
        return redirect("/sales")

    if request.method == "POST":

        try:

            product_id = int(request.form["product_id"])
            customer_id = int(request.form["customer_id"])
            quantity = int(request.form["quantity"])
            discount = float(request.form.get("discount", sale["discount"]))
            gst_rate = float(request.form.get("gst_rate", sale["gst_rate"]))
            payment_amount = float(request.form.get("payment_amount", sale["payment_amount"]))
            discount = float(request.form.get("discount", sale["discount"]))
            gst_rate = float(request.form.get("gst_rate", sale["gst_rate"]))

        except (KeyError, TypeError, ValueError):

            conn.close()
            flash("Please enter valid sale values.", "danger")
            return redirect(f"/edit-sale/{id}")

        if quantity <= 0:

            conn.close()
            flash("Sale quantity must be greater than zero.", "danger")
            return redirect(f"/edit-sale/{id}")

        payment_method = request.form.get("payment_method", sale["payment_method"])
        payment_status = request.form.get("payment_status", sale["payment_status"])
        transaction_id = request.form.get("transaction_id", sale["transaction_id"] or "").strip()
        payment_date = request.form.get("payment_date") or sale["payment_date"]
        payment_methods = {"Cash", "UPI", "Credit Card", "Debit Card", "Net Banking"}
        payment_statuses = {"Paid", "Pending", "Partially Paid"}

        if payment_method not in payment_methods or payment_status not in payment_statuses:

            conn.close()
            flash("Please select a valid payment method and status.", "danger")
            return redirect(f"/edit-sale/{id}")

        if discount < 0 or gst_rate < 0:

            conn.close()
            flash("Discount and GST rate cannot be negative.", "danger")
            return redirect(f"/edit-sale/{id}")

        if discount < 0 or gst_rate < 0:

            conn.close()
            flash("Discount and GST rate cannot be negative.", "danger")
            return redirect(f"/edit-sale/{id}")

        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        customer = cursor.fetchone()

        if product is None or customer is None:

            conn.close()
            flash("Product or customer not found.", "danger")
            return redirect(f"/edit-sale/{id}")

        available_quantity = product["quantity"]

        if product_id == sale["product_id"]:
            available_quantity += sale["quantity"]

        if quantity > available_quantity:

            conn.close()
            flash(f"Only {available_quantity} units available.", "danger")
            return redirect(f"/edit-sale/{id}")

        total = quantity * product["price"]

        if discount > total:

            conn.close()
            flash("Discount cannot be greater than the sale subtotal.", "danger")
            return redirect(f"/edit-sale/{id}")

        taxable_amount = total - discount
        gst = taxable_amount * gst_rate / 100
        grand_total = taxable_amount + gst

        if payment_amount < 0 or payment_amount > grand_total:

            conn.close()
            flash("Payment amount must be between 0 and the final amount.", "danger")
            return redirect(f"/edit-sale/{id}")

        cursor.execute("""
            UPDATE products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (sale["quantity"], sale["product_id"]))

        cursor.execute("""
            UPDATE products
            SET quantity = quantity - ?
            WHERE product_id = ?
        """, (quantity, product_id))

        cursor.execute("""
            UPDATE sales
            SET product_id = ?, customer_id = ?, quantity = ?, price = ?, total = ?,
                discount = ?, gst_rate = ?, gst = ?, grand_total = ?,
                payment_method = ?, payment_amount = ?, payment_status = ?,
                payment_date = ?, transaction_id = ?
            WHERE sale_id = ?
        """, (
            product_id,
            customer_id,
            quantity,
            product["price"],
            total,
            discount,
            gst_rate,
            gst,
            grand_total,
            payment_method,
            payment_amount,
            payment_status,
            payment_date,
            transaction_id,
            id
        ))

        conn.commit()
        conn.close()
        flash("Sale updated and stock adjusted successfully!", "success")
        return redirect("/sales")

    cursor.execute("""
        SELECT * FROM products
        WHERE quantity > 0 OR product_id = ?
        ORDER BY product_name
    """, (sale["product_id"],))
    products = cursor.fetchall()

    cursor.execute("SELECT * FROM customers ORDER BY customer_name")
    customers = cursor.fetchall()
    conn.close()

    return render_template(
        "edit_sale.html",
        sale=sale,
        products=products,
        customers=customers
    )


# =========================================================
# RETURNS MANAGEMENT
# =========================================================

@app.route("/returns", methods=["GET", "POST"])
def returns_management():

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":

        try:

            sale_id = int(request.form["sale_id"])
            quantity = int(request.form["quantity"])
            reason = request.form["reason"].strip()

        except (KeyError, TypeError, ValueError):

            conn.close()
            flash("Please enter valid return details.", "danger")
            return redirect("/returns")

        if quantity <= 0 or not reason:

            conn.close()
            flash("Return quantity and reason are required.", "danger")
            return redirect("/returns")

        cursor.execute("SELECT * FROM sales WHERE sale_id = ?", (sale_id,))
        sale = cursor.fetchone()

        if sale is None:

            conn.close()
            flash("Sale not found.", "danger")
            return redirect("/returns")

        returned_quantity = cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0)
            FROM returns
            WHERE sale_id = ?
        """, (sale_id,)).fetchone()[0]

        remaining_quantity = sale["quantity"] - returned_quantity

        if quantity > remaining_quantity:

            conn.close()
            flash(
                f"Only {remaining_quantity} units are available for return.",
                "danger"
            )
            return redirect("/returns")

        refund_amount = (
            sale["grand_total"] / sale["quantity"]
        ) * quantity

        cursor.execute("""
            INSERT INTO returns
            (sale_id, product_id, quantity, refund_amount, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            sale_id,
            sale["product_id"],
            quantity,
            refund_amount,
            reason
        ))

        cursor.execute("""
            UPDATE products
            SET quantity = quantity + ?
            WHERE product_id = ?
        """, (quantity, sale["product_id"]))

        conn.commit()
        conn.close()
        flash("Return recorded and inventory restored successfully!", "success")
        return redirect("/returns")

    sales = cursor.execute("""
        SELECT
            sales.sale_id,
            sales.quantity AS sold_quantity,
            sales.grand_total,
            products.product_name,
            customers.customer_name,
            COALESCE(SUM(returns.quantity), 0) AS returned_quantity
        FROM sales
        JOIN products ON sales.product_id = products.product_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
        LEFT JOIN returns ON sales.sale_id = returns.sale_id
        GROUP BY sales.sale_id
        ORDER BY sales.sale_id DESC
    """).fetchall()

    return_history = cursor.execute("""
        SELECT
            returns.return_id,
            returns.quantity,
            returns.refund_amount,
            returns.reason,
            returns.return_date,
            sales.sale_id,
            products.product_name,
            customers.customer_name
        FROM returns
        JOIN sales ON returns.sale_id = sales.sale_id
        JOIN products ON returns.product_id = products.product_id
        LEFT JOIN customers ON sales.customer_id = customers.customer_id
        ORDER BY returns.return_id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "returns.html",
        sales=sales,
        return_history=return_history
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
            sales.discount,
            sales.gst_rate,
            sales.gst,
            sales.grand_total,
            sales.payment_method,
            sales.payment_amount,
            sales.payment_status,
            sales.payment_date,
            sales.transaction_id,
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
    discount = sale["discount"]
    gst_rate = sale["gst_rate"]
    gst = sale["gst"]
    grand_total = sale["grand_total"]

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