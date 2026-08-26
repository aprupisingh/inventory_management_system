# 📦 Inventory Management System

A web-based **Inventory Management System** developed using **Python, Flask, SQLite, HTML, CSS, Bootstrap, and Jinja2**.

This application provides a simple and user-friendly platform for managing products, categories, inventory stock, customers, sales, billing, invoices, and sales history.

---

## 🚀 Live Demo

🔗 **Live Application:**
https://inventory-management-system-six-olive.vercel.app/

---

## 📌 Project Overview

The Inventory Management System is designed to simplify inventory and sales operations for small businesses.

The application allows users to manage products and categories, maintain customer information, record sales transactions, automatically update inventory stock, and generate invoices.

The project also includes a dashboard that provides important business metrics such as total products, categories, low-stock items, inventory value, total sales, and revenue.

---

## ✨ Features

### 📦 Product Management

* ➕ Add new products
* 👁️ View all products
* 🔍 Search products
* ✏️ Edit product details
* 🗑️ Delete products
* 📊 Track product quantity
* 💰 Manage product prices
* 📂 Organize products by category

### 📊 Dashboard

The dashboard provides an overview of important inventory and sales information:

* 📦 Total Products
* 📂 Total Categories
* ⚠️ Low Stock Items
* 💰 Total Inventory Value
* 🧾 Total Sales
* 💵 Total Revenue

### 🛒 Sales Management

* ➕ Create new sales
* 👤 Enter customer details
* 📦 Select products
* 🔢 Enter quantity
* 💰 Automatically calculate total price
* 📉 Automatically reduce inventory stock
* 🕒 Store sale date and time

### 👤 Customer Management

* Add customer details
* Store customer names
* Store customer phone numbers
* View customer information
* Associate customer information with sales

### 🧾 Billing & Invoice

* Generate bills
* Generate invoices
* Display customer information
* Display purchased products
* Display quantity and price
* Calculate total amount
* Store sales/invoice information

### 📈 Sales History

* View previous sales
* Search sales
* View customer details
* View product details
* View sale date and time
* View total revenue

---

## 🛠️ Technologies Used

| Technology    | Purpose                   |
| ------------- | ------------------------- |
| 🐍 Python     | Backend programming       |
| 🌐 Flask      | Web application framework |
| 🗄️ SQLite    | Database management       |
| 🎨 HTML5      | Page structure            |
| 🎨 CSS3       | Styling                   |
| 🅱️ Bootstrap | Responsive user interface |
| 🔤 Jinja2     | Dynamic HTML templates    |
| 🧮 SQL        | Database operations       |
| 🚀 Vercel     | Deployment                |

---

## 🏗️ Application Workflow

```text
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Web Browser   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Flask Application│
                    └────────┬────────┘
                             │
             ┌───────────────┼───────────────┐
             │               │               │
             ▼               ▼               ▼
        Products         Customers         Sales
             │               │               │
             └───────────────┼───────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ SQLite Database │
                    └─────────────────┘
```

---

## 🗄️ Database

The application uses **SQLite** for storing inventory and sales-related data.

The main data entities include:

### Products

Stores information about inventory products, including:

* Product ID
* Product name
* Category
* Price
* Quantity

### Categories

Stores product category information.

### Customers

Stores:

* Customer name
* Customer phone number

### Sales

Stores transaction information including:

* Customer
* Product
* Quantity
* Price
* Total amount
* Sale date and time

---

## 📊 Business Metrics

The dashboard provides several useful business metrics.

### Inventory Metrics

* Total number of products
* Total categories
* Low-stock products
* Total inventory value

### Sales Metrics

* Total number of sales
* Total revenue
* Sales history
* Transaction date and time

These metrics can help a business monitor inventory levels and understand basic sales performance.

---

## 📁 Project Structure

```text
inventory_management_system/
│
├── templates/
│   ├── HTML templates
│   └── ...
│
├── .vscode/
│
├── app.py
├── main.py
├── database.py
├── inventory.db
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/aprupisingh/inventory_management_system.git
```

### 2. Navigate to the project directory

```bash
cd inventory_management_system
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

If your application is started through `main.py`, use:

```bash
python main.py
```

### 7. Open the application

```text
http://127.0.0.1:5000/
```

---

## 📸 Screenshots

Add screenshots of the actual application here.

### 📊 Dashboard

```markdown
![Dashboard](screenshots/dashboard.png)
```

### 📦 Product Management

```markdown
![Products](screenshots/products.png)
```

### 🛒 Sales Management

```markdown
![Sales](screenshots/sales.png)
```

### 🧾 Invoice

```markdown
![Invoice](screenshots/invoice.png)
```

### 📈 Sales History

```markdown
![Sales History](screenshots/sales-history.png)
```

---

## 🎯 Project Objectives

The main objectives of this project are:

* Build a practical inventory management application
* Implement CRUD operations
* Work with a relational database
* Practice SQL and database operations
* Connect Python with SQLite
* Develop a Flask web application
* Create a responsive interface using Bootstrap
* Implement sales and billing functionality
* Automatically update inventory after sales
* Display useful business metrics

---

## 💡 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Flask
* SQL
* SQLite
* Database Design
* CRUD Operations
* HTML
* CSS
* Bootstrap
* Jinja2
* Backend Development
* Business Logic
* Inventory Management
* Sales Management
* Data Management
* Web Application Development
* Deployment

---

## 🔮 Future Improvements

Planned improvements include:

* 📊 Advanced sales analytics
* 📈 Power BI dashboard integration
* 📥 Export sales reports to Excel/CSV
* 🔐 User authentication and authorization
* 📧 Low-stock notifications
* 🌐 REST API integration
* 🗄️ MySQL/PostgreSQL support
* 👥 Advanced customer analytics
* 📊 Product performance analysis
* 📱 Improved mobile responsiveness

---

## 👨‍💻 Author

### Aprupinath Singh

**Aspiring Data Analyst | Python | SQL | Power BI**

🔗 GitHub:
https://github.com/aprupisingh

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project was developed for **educational and portfolio purposes**.
