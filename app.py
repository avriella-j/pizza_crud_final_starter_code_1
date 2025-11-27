import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Database setup
DB_PATH = os.path.join('data', 'pizzas.db')

# Create data directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

def get_db_connection():
    """Get a connection to the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create database tables if they don't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create Pizza table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Pizza (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        ''')
        
        # Create PromoCode table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS PromoCode (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                discount_percent REAL NOT NULL,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                usage_limit INTEGER,
                times_used INTEGER DEFAULT 0
            )
        ''')
        
        # Create Order table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS "Order" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pizza_id INTEGER,
                quantity INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                promo_code_id INTEGER,
                FOREIGN KEY (pizza_id) REFERENCES Pizza (id),
                FOREIGN KEY (promo_code_id) REFERENCES PromoCode (id)
            )
        ''')
        
        # Add sample pizzas if table is empty
        cursor.execute('SELECT COUNT(*) FROM Pizza')
        if cursor.fetchone()[0] == 0:
            sample_pizzas = [
                ('Margherita', 14.99),
                ('Pepperoni', 1.99),
                ('Hawaiian', 99.99),
                ('Vegetarian', 12.99),
                ('Supreme', 14.99),
                ('BBQ Chicken', 13.99),
                ('Meat Lovers', 15.99),
                ('Buffalo', 16.99)
            ]
            cursor.executemany('INSERT INTO Pizza (name, price) VALUES (?, ?)', sample_pizzas)
            conn.commit()
        
        # Add promo codes if table is empty
        cursor.execute('SELECT COUNT(*) FROM PromoCode')
        if cursor.fetchone()[0] == 0:
            # -1 for usage_limit means unlimited
            promo_codes = [
                ('WELCOME10', 10.0, None, None, -1, 0),
                ('MIDWEEK15', 15.0, None, None, 200, 0),
                ('FAMILY20', 20.0, None, None, 150, 0)
            ]
            cursor.executemany('''
                INSERT INTO PromoCode (code, discount_percent, start_date, end_date, usage_limit, times_used) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', promo_codes)
            conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'conn' in locals():
            conn.close()

def get_all_pizzas():
    """Get all pizzas from the database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, price FROM Pizza ORDER BY id')
        return cursor.fetchall()
    finally:
        conn.close()

def validate_promo_code(code):
    """Validate promo code and return promo details if valid, None otherwise"""
    if not code:
        return None
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, code, discount_percent, start_date, end_date, usage_limit, times_used
            FROM PromoCode
            WHERE UPPER(code) = UPPER(?)
        ''', (code,))
        promo = cursor.fetchone()
        
        if not promo:
            return None
        
        # Check if usage limit is reached (NULL or -1 means unlimited)
        if promo['usage_limit'] is not None and promo['usage_limit'] != -1:
            if promo['times_used'] >= promo['usage_limit']:
                return None
        
        # Check date validity (if dates are set)
        current_date = datetime.now()
        if promo['start_date'] and datetime.strptime(promo['start_date'], '%Y-%m-%d %H:%M:%S') > current_date:
            return None
        if promo['end_date'] and datetime.strptime(promo['end_date'], '%Y-%m-%d %H:%M:%S') < current_date:
            return None
        
        return promo
    finally:
        conn.close()

def increment_promo_usage(promo_id):
    """Increment the times_used counter for a promo code"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE PromoCode
            SET times_used = times_used + 1
            WHERE id = ?
        ''', (promo_id,))
        conn.commit()
    finally:
        conn.close()

def save_order(pizza_id, quantity, customer_name, promo_code=None):
    """Save order to database and return order ID"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        promo_code_id = None
        
        # Validate and apply promo code if provided
        if promo_code:
            promo = validate_promo_code(promo_code)
            if promo:
                promo_code_id = promo['id']
                increment_promo_usage(promo_code_id)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO "Order" (pizza_id, quantity, customer_name, timestamp, promo_code_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (pizza_id, quantity, customer_name, current_time, promo_code_id))
        
        order_id = cursor.lastrowid
        conn.commit()
        return order_id
    finally:
        conn.close()

def get_order_details(order_id):
    """Get order details from database"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, p.name, p.price, o.quantity, o.customer_name, 
                   o.timestamp, pc.code, pc.discount_percent
            FROM "Order" o
            JOIN Pizza p ON o.pizza_id = p.id
            LEFT JOIN PromoCode pc ON o.promo_code_id = pc.id
            WHERE o.id = ?
        ''', (order_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_pizza_image_filename(pizza_name):
    """Map pizza names to their actual image filenames"""
    # Mapping for pizzas with special filename cases
    image_map = {
        'Margherita': 'margharita.avif',  # Misspelled in filename
        'BBQ Chicken': 'bbq_chicken.avif',  # Underscore instead of space
        'Meat Lovers': 'meat lovers.avif',  # Space in filename
        'Supreme': 'Supreme.jpg',  # Capital S and .jpg extension
    }
    
    # Return mapped filename or generate default
    if pizza_name in image_map:
        return image_map[pizza_name]
    else:
        # Default: lowercase, no spaces, .avif extension
        return pizza_name.lower().replace(' ', '') + '.avif'

# Routes
@app.route('/')
def menu():
    """Show the pizza menu and order form"""
    pizzas = get_all_pizzas()
    # Add image filename to each pizza
    pizzas_with_images = []
    for pizza in pizzas:
        pizza_dict = dict(pizza)
        pizza_dict['image_filename'] = get_pizza_image_filename(pizza['name'])
        pizzas_with_images.append(pizza_dict)
    return render_template('menu.html', pizzas=pizzas_with_images)

@app.route('/order', methods=['POST'])
def create_order():
    """Process the pizza order"""
    pizza_id = request.form.get('pizza_id')
    quantity = request.form.get('quantity')
    customer_name = request.form.get('customer_name')
    promo_code = request.form.get('promo_code', '').strip()
    
    if not pizza_id or not quantity or not customer_name:
        return redirect(url_for('menu'))
    
    # Save order with optional promo code
    order_id = save_order(pizza_id, quantity, customer_name, promo_code if promo_code else None)
    
    if not order_id:
        return redirect(url_for('menu'))
    
    return redirect(url_for('confirmation', order_id=order_id))

@app.route('/confirmation')
def confirmation():
    """Show order confirmation"""
    order_id = request.args.get('order_id')
    if not order_id:
        return redirect(url_for('menu'))
        
    order = get_order_details(order_id)
    if not order:
        return redirect(url_for('menu'))
    
    # Calculate totals
    subtotal = order[2] * order[3]
    discount_amount = 0
    
    if order[6]:  # If promo code exists
        discount_amount = subtotal * (order[7] / 100)
    
    final_total = subtotal - discount_amount
    
    order_data = {
        'order_id': order[0],
        'pizza_name': order[1],
        'price': order[2],
        'quantity': order[3],
        'customer_name': order[4],
        'timestamp': order[5],
        'promo_code': order[6],
        'discount_percent': order[7],
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'final_total': final_total
    }
    
    return render_template('confirmation.html', 
                         order=order_data, 
                         display_date=order[5])

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
                       

