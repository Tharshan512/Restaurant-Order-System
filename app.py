from flask import Flask, render_template
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

if __name__ == '__main__':
    app.run(debug=True)