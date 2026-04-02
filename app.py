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

if __name__ == '__main__':
    app.run(debug=True)