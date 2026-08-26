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
<img width="1879" height="1002" alt="image" src="https://github.com/user-attachments/assets/b6fe3ee9-afc2-4e52-96a5-4b5625d93048" />

### 📦 Product Management

<img width="512" height="613" alt="image" src="https://github.com/user-attachments/assets/a235c8c4-6bc9-4c97-98a2-f1d2b2e0b440" /><img width="1836" height="713" alt="image" src="https://github.com/user-attachments/assets/290996cb-37a0-4622-8150-556a1a657a46" />


### 🛒 Sales Management

<img width="1536" height="888" alt="image" src="https://github.com/user-attachments/assets/8f0eba11-362d-420b-bfc6-3086cca7b727" />

### 🧾 Invoice

<img width="1869" height="926" alt="image" src="https://github.com/user-attachments/assets/8f80948b-781e-4e64-9401-67559c2f376a" />


### 📈 Sales History

<img width="1871" height="871" alt="image" src="https://github.com/user-attachments/assets/3e5b0fd6-45d8-4e53-9874-46fadfdb645d" />
## 🗂️Report
<img width="1869" height="926" alt="image" src="https://github.com/user-attachments/assets/f3a5aed0-6c21-4599-95dc-8f2aefc94872" />


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

