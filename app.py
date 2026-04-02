from flask import Flask, render_template, request, redirect, url_for
from db_config import get_db_connection

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/test-db')
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    conn.close()
    return f"Connected to database: {result[0]}"

@app.route('/order-details')
def order_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        o.OrderID,
        CONCAT(c.FirstName, ' ', c.LastName) AS Customer,
        m.ItemName,
        oi.Quantity,
        m.Price,
        (oi.Quantity * m.Price) AS Subtotal
    FROM Orders o
    JOIN Customer c ON o.CustomerID = c.CustomerID
    JOIN OrderItem oi ON o.OrderID = oi.OrderID
    JOIN MenuItem m ON oi.MenuItemID = m.MenuItemID
    """

    cursor.execute(query)
    orders = cursor.fetchall()

    conn.close()
    return render_template('order_details.html', orders=orders)

@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Customer")
    customers = cursor.fetchall()

    conn.close()

    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Customer (FirstName, LastName, Phone) VALUES (%s, %s, %s)",
            (first_name, last_name, phone)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('view_customers'))

    return render_template('add_customer.html')

@app.route('/customers/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']

        cursor.execute("""
            UPDATE Customer
            SET FirstName = %s, LastName = %s, Phone = %s
            WHERE CustomerID = %s
        """, (first_name, last_name, phone, id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_customers'))

    cursor.execute("SELECT * FROM Customer WHERE CustomerID = %s", (id,))
    customer = cursor.fetchone()

    conn.close()
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/delete/<int:id>')
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Customer WHERE CustomerID = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_customers'))

@app.route('/categories')
def view_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Category")
    categories = cursor.fetchall()

    conn.close()

    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['category_name']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO Category (CategoryName) VALUES (%s)",
            (name,)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('view_categories'))

    return render_template('add_category.html')

@app.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
def edit_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['category_name']

        cursor.execute("""
            UPDATE Category
            SET CategoryName = %s
            WHERE CategoryID = %s
        """, (name, id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_categories'))

    cursor.execute("SELECT * FROM Category WHERE CategoryID = %s", (id,))
    category = cursor.fetchone()

    conn.close()
    return render_template('edit_category.html', category=category)

@app.route('/categories/delete/<int:id>')
def delete_category(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Category WHERE CategoryID = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_categories'))

@app.route('/menu-items')
def view_menu_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MenuItem.MenuItemID, MenuItem.ItemName, MenuItem.Price, MenuItem.Description, Category.CategoryName
        FROM MenuItem
        JOIN Category ON MenuItem.CategoryID = Category.CategoryID
    """)
    menu_items = cursor.fetchall()

    conn.close()

    return render_template('menu_items.html', menu_items=menu_items)

@app.route('/menu-items/add', methods=['GET', 'POST'])
def add_menu_item():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        item_name = request.form['item_name']
        price = request.form['price']
        description = request.form['description']
        category_id = request.form['category_id']

        cursor.execute("""
            INSERT INTO MenuItem (ItemName, Price, Description, CategoryID)
            VALUES (%s, %s, %s, %s)
        """, (item_name, price, description, category_id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_menu_items'))

    cursor.execute("SELECT CategoryID, CategoryName FROM Category")
    categories = cursor.fetchall()

    conn.close()
    return render_template('add_menu_item.html', categories=categories)

@app.route('/menu-items/edit/<int:id>', methods=['GET', 'POST'])
def edit_menu_item(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        item_name = request.form['item_name']
        price = request.form['price']
        description = request.form['description']
        category_id = request.form['category_id']

        cursor.execute("""
            UPDATE MenuItem
            SET ItemName = %s, Price = %s, Description = %s, CategoryID = %s
            WHERE MenuItemID = %s
        """, (item_name, price, description, category_id, id))

        conn.commit()
        conn.close()

        return redirect(url_for('view_menu_items'))

    cursor.execute("SELECT * FROM MenuItem WHERE MenuItemID = %s", (id,))
    menu_item = cursor.fetchone()

    cursor.execute("SELECT CategoryID, CategoryName FROM Category")
    categories = cursor.fetchall()

    conn.close()
    return render_template('edit_menu_item.html', menu_item=menu_item, categories=categories)

@app.route('/menu-items/delete/<int:id>')
def delete_menu_item(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM MenuItem WHERE MenuItemID = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_menu_items'))

if __name__ == '__main__':
    app.run(debug=True)