from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def connect_db():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home Page


@app.route("/")
def home():

    conn = connect_db()
    cursor = conn.cursor()

    # Products
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Total Products
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    # Total Categories
    cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
    total_categories = cursor.fetchone()[0]

    # Low Stock
    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
    low_stock = cursor.fetchone()[0]

    # Inventory Value
    cursor.execute("SELECT SUM(quantity * price) FROM products")
    total_value = cursor.fetchone()[0]

    if total_value is None:
        total_value = 0

    conn.close()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value
    )
# Add Product
@app.route("/add", methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        price = request.form["price"]

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO products(product_name,category,quantity,price)
            VALUES(?,?,?,?)
            """,
            (name, category, quantity, price),
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_product.html")


# Search Product
@app.route("/search")
def search():

    keyword = request.args.get("keyword")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE product_name LIKE ?
        OR category LIKE ?
    """, ('%'+keyword+'%', '%'+keyword+'%'))

    products = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
    total_categories = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM products WHERE quantity < 10")
    low_stock = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantity * price) FROM products")
    total_value = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_categories=total_categories,
        low_stock=low_stock,
        total_value=total_value
    )

# Edit Product
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        price = request.form["price"]

        cursor.execute(
            """
            UPDATE products
            SET product_name=?,
                category=?,
                quantity=?,
                price=?
            WHERE product_id=?
            """,
            (name, category, quantity, price, id),
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM products WHERE product_id=?",
        (id,),
    )

    product = cursor.fetchone()

    conn.close()

    return render_template("edit_product.html", product=product)


# Delete Product
@app.route("/delete/<int:id>")
def delete(id):

    conn = connect_db()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM products WHERE product_id=?",
        (id,),
    )

    conn.commit()

    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)