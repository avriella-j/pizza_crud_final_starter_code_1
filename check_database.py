import sqlite3

# Connect to the database
conn = sqlite3.connect('data/pizzas.db')
cursor = conn.cursor()

# Show all tables
print("=" * 50)
print("DATABASE STRUCTURE")
print("=" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\nTables in database: {[table[0] for table in tables]}")

# Show Pizza table structure
print("\n" + "=" * 50)
print("PIZZA TABLE")
print("=" * 50)
cursor.execute("PRAGMA table_info(Pizza)")
columns = cursor.fetchall()
print("\nColumns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Show all pizzas
cursor.execute("SELECT * FROM Pizza")
pizzas = cursor.fetchall()
print(f"\nTotal Pizzas: {len(pizzas)}")
print("\nPizza Data:")
for pizza in pizzas:
    print(f"  ID: {pizza[0]}, Name: {pizza[1]}, Price: ${pizza[2]:.2f}")

# Show Order table structure
print("\n" + "=" * 50)
print("ORDER TABLE")
print("=" * 50)
cursor.execute("PRAGMA table_info('Order')")
columns = cursor.fetchall()
print("\nColumns:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Show order count
cursor.execute('SELECT COUNT(*) FROM "Order"')
order_count = cursor.fetchone()[0]
print(f"\nTotal Orders: {order_count}")

# Show recent orders if any
if order_count > 0:
    cursor.execute('''
        SELECT o.id, o.customer_name, p.name, o.quantity, o.order_date
        FROM "Order" o
        JOIN Pizza p ON o.pizza_id = p.id
        ORDER BY o.order_date DESC
        LIMIT 5
    ''')
    orders = cursor.fetchall()
    print("\nRecent Orders:")
    for order in orders:
        print(f"  Order #{order[0]}: {order[1]} ordered {order[3]}x {order[2]} on {order[4]}")

conn.close()
print("\n" + "=" * 50)
