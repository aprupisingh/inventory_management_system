import sqlite3


# Connect to database
def connect_db():
    return sqlite3.connect("inventory.db")


# Add Product
def add_product():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        product_name = input("Enter Product Name: ")
        category = input("Enter Category: ")
        quantity = int(input("Enter Quantity: "))
        price = float(input("Enter Price: "))

        cursor.execute(
            """
            INSERT INTO products(product_name, category, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (product_name, category, quantity, price)
        )

        conn.commit()
        print("\nProduct Added Successfully!")

    except ValueError:
        print("\nPlease enter valid numbers for quantity and price.")

    finally:
        conn.close()


# View All Products
def view_products():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    if len(products) == 0:
        print("\nNo products available.")

    else:
        print("\n============== PRODUCT LIST ==============")
        print("{:<8} {:<20} {:<15} {:<10} {:<10}".format(
            "ID", "Name", "Category", "Qty", "Price"
        ))
        print("-" * 70)

        for product in products:
            print("{:<8} {:<20} {:<15} {:<10} {:<10.2f}".format(
                product[0],
                product[1],
                product[2],
                product[3],
                product[4]
            ))

    conn.close()


# Search Product
def search_product():
    conn = connect_db()
    cursor = conn.cursor()

    search_value = input("Enter Product ID or Product Name: ")

    if search_value.isdigit():
        cursor.execute(
            "SELECT * FROM products WHERE product_id=?",
            (int(search_value),)
        )
    else:
        cursor.execute(
            "SELECT * FROM products WHERE product_name LIKE ?",
            ("%" + search_value + "%",)
        )

    products = cursor.fetchall()

    if len(products) == 0:
        print("\nProduct not found!")

    else:
        print("\n============== SEARCH RESULT ==============")
        print("{:<8} {:<20} {:<15} {:<10} {:<10}".format(
            "ID", "Name", "Category", "Qty", "Price"
        ))
        print("-" * 70)

        for product in products:
            print("{:<8} {:<20} {:<15} {:<10} {:<10.2f}".format(
                product[0],
                product[1],
                product[2],
                product[3],
                product[4]
            ))

    conn.close()


# Update Product
def update_product():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        product_id = int(input("Enter Product ID to update: "))

        cursor.execute(
            "SELECT * FROM products WHERE product_id=?",
            (product_id,)
        )

        product = cursor.fetchone()

        if product is None:
            print("Product not found!")
            conn.close()
            return

        print("Leave blank to keep old value.")

        name = input("Enter New Name: ")
        category = input("Enter New Category: ")
        quantity = input("Enter New Quantity: ")
        price = input("Enter New Price: ")

        if name == "":
            name = product[1]

        if category == "":
            category = product[2]

        if quantity == "":
            quantity = product[3]
        else:
            quantity = int(quantity)

        if price == "":
            price = product[4]
        else:
            price = float(price)

        cursor.execute(
            """
            UPDATE products
            SET product_name=?, category=?, quantity=?, price=?
            WHERE product_id=?
            """,
            (name, category, quantity, price, product_id)
        )

        conn.commit()

        print("Product Updated Successfully!")

    except ValueError:
        print("Invalid input!")

    finally:
        conn.close()


# Delete Product
def delete_product():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        product_id = int(input("Enter Product ID to delete: "))

        cursor.execute(
            "DELETE FROM products WHERE product_id=?",
            (product_id,)
        )

        conn.commit()

        print("Product Deleted Successfully!")

    except ValueError:
        print("Enter a valid Product ID.")

    finally:
        conn.close()


# Main Menu
while True:

    print("\n========== Inventory Management System ==========")
    print("1. Add Product")
    print("2. View Products")
    print("3. Search Product")
    print("4. Update Product")
    print("5. Delete Product")
    print("6. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_product()

    elif choice == "2":
        view_products()

    elif choice == "3":
        search_product()

    elif choice == "4":
        update_product()

    elif choice == "5":
        delete_product()

    elif choice == "6":
        print("Thank you for using Inventory Management System.")
        break

    else:
        print("Invalid Choice!")