import sqlite3
import os

DB_PATH = os.path.join('data', 'pizzas.db')

def verify_schema():
    """Verify the Order table has the correct schema"""
    print("=" * 70)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 70)
    
    if not os.path.exists(DB_PATH):
        print("❌ Database not found!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get Order table schema
        cursor.execute("PRAGMA table_info('Order')")
        columns = cursor.fetchall()
        
        print("\nOrder Table Schema:")
        print("-" * 70)
        for col in columns:
            print(f"  {col[1]:20} {col[2]:15} {'NOT NULL' if col[3] else ''}")
        
        # Expected columns
        expected_columns = {
            'id': 'INTEGER',
            'pizza_id': 'INTEGER',
            'quantity': 'INTEGER',
            'customer_name': 'TEXT',
            'timestamp': 'TIMESTAMP',
            'promo_code_id': 'INTEGER'
        }
        
        actual_columns = {col[1]: col[2] for col in columns}
        
        print("\nVerification:")
        print("-" * 70)
        
        all_correct = True
        for col_name, col_type in expected_columns.items():
            if col_name in actual_columns:
                if actual_columns[col_name] == col_type:
                    print(f"  ✅ {col_name:20} {col_type}")
                else:
                    print(f"  ❌ {col_name:20} Expected: {col_type}, Got: {actual_columns[col_name]}")
                    all_correct = False
            else:
                print(f"  ❌ {col_name:20} MISSING")
                all_correct = False
        
        # Check for unexpected columns
        for col_name in actual_columns:
            if col_name not in expected_columns:
                print(f"  ⚠️  {col_name:20} UNEXPECTED COLUMN")
                all_correct = False
        
        # Check sample data
        cursor.execute('SELECT COUNT(*) FROM "Order"')
        order_count = cursor.fetchone()[0]
        print(f"\nTotal Orders: {order_count}")
        
        if order_count > 0:
            print("\nSample Order:")
            print("-" * 70)
            cursor.execute('''
                SELECT o.id, o.pizza_id, o.quantity, o.customer_name, 
                       o.timestamp, o.promo_code_id
                FROM "Order" o
                LIMIT 1
            ''')
            order = cursor.fetchone()
            print(f"  ID: {order[0]}")
            print(f"  Pizza ID: {order[1]}")
            print(f"  Quantity: {order[2]}")
            print(f"  Customer Name: {order[3]}")
            print(f"  Timestamp: {order[4]}")
            print(f"  Promo Code ID: {order[5]}")
        
        print("\n" + "=" * 70)
        if all_correct:
            print("✅ SCHEMA IS CORRECT!")
        else:
            print("❌ SCHEMA HAS ISSUES!")
        print("=" * 70)
        
    finally:
        conn.close()

if __name__ == '__main__':
    verify_schema()
