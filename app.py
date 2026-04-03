from flask import Flask, render_template, request, redirect, url_for
from db_config import get_db_connection

def update_order_total(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(oi.Quantity * m.Price)
        FROM OrderItem oi
        JOIN MenuItem m ON oi.MenuItemID = m.MenuItemID
        WHERE oi.OrderID = %s
    """, (order_id,))

    total = cursor.fetchone()[0]

    if total is None:
        total = 0.00

    cursor.execute("""
        UPDATE Orders
        SET TotalAmount = %s
        WHERE OrderID = %s
    """, (total, order_id))

    conn.commit()
    conn.close()
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

    cursor.execute("""
        SELECT 
            o.OrderID,
            CONCAT(c.FirstName, ' ', c.LastName) AS Customer,
            GROUP_CONCAT(m.ItemName SEPARATOR ', ') AS Items,
            SUM(oi.Quantity) AS TotalQuantity,
        SUM(oi.Quantity * m.Price) AS TotalAmount
        FROM Orders o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        JOIN OrderItem oi ON o.OrderID = oi.OrderID
        JOIN MenuItem m ON oi.MenuItemID = m.MenuItemID
        GROUP BY o.OrderID, Customer
    """)
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

@app.route('/orders')
def view_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT o.OrderID, o.OrderDate, o.Status, o.TotalAmount,
               c.FirstName, c.LastName,
               s.FirstName, s.LastName
        FROM Orders o
        JOIN Customer c ON o.CustomerID = c.CustomerID
        JOIN Staff s ON o.StaffID = s.StaffID
    """)
    orders = cursor.fetchall()

    conn.close()
    return render_template('orders.html', orders=orders)

@app.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        order_date = request.form['order_date']
        status = request.form['status']
        customer_id = request.form['customer_id']
        staff_id = request.form['staff_id']

        cursor.execute("""
            INSERT INTO Orders (OrderDate, Status, TotalAmount, CustomerID, StaffID)
            VALUES (%s, %s, %s, %s, %s)
        """, (order_date, status, 0.00, customer_id, staff_id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_orders'))

    cursor.execute("SELECT CustomerID, FirstName, LastName FROM Customer")
    customers = cursor.fetchall()

    cursor.execute("SELECT StaffID, FirstName, LastName FROM Staff")
    staff = cursor.fetchall()

    conn.close()
    return render_template('add_order.html', customers=customers, staff=staff)

@app.route('/orders/edit/<int:id>', methods=['GET', 'POST'])
def edit_order(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        status = request.form['status']

        cursor.execute("""
            UPDATE Orders
            SET Status = %s
            WHERE OrderID = %s
        """, (status, id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_orders'))

    cursor.execute("SELECT * FROM Orders WHERE OrderID = %s", (id,))
    order = cursor.fetchone()

    conn.close()
    return render_template('edit_order.html', order=order)

@app.route('/orders/delete/<int:id>')
def delete_order(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM OrderItem WHERE OrderID = %s", (id,))
    cursor.execute("DELETE FROM Orders WHERE OrderID = %s", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for('view_orders'))

@app.route('/orders/<int:order_id>/items', methods=['GET', 'POST'])
def manage_order_items(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        menu_item_id = request.form['menu_item_id']
        quantity = request.form['quantity']

        cursor.execute("""
            INSERT INTO OrderItem (OrderID, MenuItemID, Quantity)
            VALUES (%s, %s, %s)
        """, (order_id, menu_item_id, quantity))

        conn.commit()

        update_order_total(order_id)

        conn.close()
        return redirect(url_for('manage_order_items', order_id=order_id))

    cursor.execute("""
        SELECT oi.OrderID, oi.MenuItemID, m.ItemName, m.Price, oi.Quantity
        FROM OrderItem oi
        JOIN MenuItem m ON oi.MenuItemID = m.MenuItemID
        WHERE oi.OrderID = %s
    """, (order_id,))
    items = cursor.fetchall()

    cursor.execute("SELECT MenuItemID, ItemName FROM MenuItem")
    menu_items = cursor.fetchall()

    conn.close()
    return render_template('manage_order_items.html', order_id=order_id, items=items, menu_items=menu_items)

@app.route('/orders/<int:order_id>/items/edit/<int:menu_item_id>', methods=['GET', 'POST'])
def edit_order_item(order_id, menu_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        quantity = request.form['quantity']

        cursor.execute("""
            UPDATE OrderItem
            SET Quantity = %s
            WHERE OrderID = %s AND MenuItemID = %s
        """, (quantity, order_id, menu_item_id))

        conn.commit()

        update_order_total(order_id)

        conn.close()
        return redirect(url_for('manage_order_items', order_id=order_id))

    cursor.execute("""
        SELECT OrderID, MenuItemID, Quantity
        FROM OrderItem
        WHERE OrderID = %s AND MenuItemID = %s
    """, (order_id, menu_item_id))
    order_item = cursor.fetchone()

    conn.close()
    return render_template('edit_order_item.html', order_item=order_item, order_id=order_id)

@app.route('/orders/<int:order_id>/items/delete/<int:menu_item_id>')
def delete_order_item(order_id, menu_item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM OrderItem
        WHERE OrderID = %s AND MenuItemID = %s
    """, (order_id, menu_item_id))

    conn.commit()

    update_order_total(order_id)

    conn.close()
    return redirect(url_for('manage_order_items', order_id=order_id))

if __name__ == '__main__':
    app.run(debug=True)