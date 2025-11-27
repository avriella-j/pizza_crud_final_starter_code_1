import sqlite3

# Connect to the database
conn = sqlite3.connect('data/pizzas.db')
cursor = conn.cursor()

# Update the prices
updates = [
    (13.99, 2),  # Pepperoni
    (13.49, 3),  # Hawaiian
    (15.49, 5),  # Supreme
]

print("Updating pizza prices...")
for price, pizza_id in updates:
    cursor.execute('UPDATE Pizza SET price = ? WHERE id = ?', (price, pizza_id))
    cursor.execute('SELECT name FROM Pizza WHERE id = ?', (pizza_id,))
    name = cursor.fetchone()[0]
    print(f"  Updated {name} (ID: {pizza_id}) to ${price:.2f}")

conn.commit()

# Verify the changes
print("\nVerifying updates:")
cursor.execute('SELECT id, name, price FROM Pizza WHERE id IN (2, 3, 5)')
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Name: {row[1]}, Price: ${row[2]:.2f}")

conn.close()
print("\nPrices updated successfully!")
