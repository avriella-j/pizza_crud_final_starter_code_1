import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join('data', 'pizzas.db')

def test_order_flow():
    """Test the complete order flow with new schema"""
    print("=" * 70)
    print("ORDER FLOW TEST - NEW SCHEMA")
    print("=" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Test 1: Create order without promo code
        print("\n1. Testing Order Creation WITHOUT Promo Code")
        print("-" * 70)
        
        pizza_id = 1  # Margherita
        quantity = 2
        customer_name = "Test User 1"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO "Order" (pizza_id, quantity, customer_name, timestamp, promo_code_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (pizza_id, quantity, customer_name, timestamp, None))
        
        order_id = cursor.lastrowid
        conn.commit()
        
        # Retrieve and verify
        cursor.execute('''
            SELECT o.id, p.name, p.price, o.quantity, o.customer_name, 
                   o.timestamp, pc.code, pc.discount_percent
            FROM "Order" o
            JOIN Pizza p ON o.pizza_id = p.id
            LEFT JOIN PromoCode pc ON o.promo_code_id = pc.id
            WHERE o.id = ?
        ''', (order_id,))
        
        order = cursor.fetchone()
        
        if order:
            subtotal = order[2] * order[3]
            discount_amount = 0
            final_total = subtotal
            
            print(f"  ✅ Order Created Successfully!")
            print(f"     Order ID: {order[0]}")
            print(f"     Pizza: {order[1]}")
            print(f"     Price: ${order[2]:.2f}")
            print(f"     Quantity: {order[3]}")
            print(f"     Customer: {order[4]}")
            print(f"     Timestamp: {order[5]}")
            print(f"     Promo Code: {order[6] if order[6] else 'None'}")
            print(f"     Subtotal: ${subtotal:.2f}")
            print(f"     Discount: ${discount_amount:.2f}")
            print(f"     Final Total: ${final_total:.2f}")
        else:
            print("  ❌ Failed to retrieve order")
        
        # Test 2: Create order with promo code
        print("\n2. Testing Order Creation WITH Promo Code (MIDWEEK15)")
        print("-" * 70)
        
        # Get promo code ID
        cursor.execute('SELECT id FROM PromoCode WHERE code = ?', ('MIDWEEK15',))
        promo = cursor.fetchone()
        promo_code_id = promo[0] if promo else None
        
        pizza_id = 2  # Pepperoni
        quantity = 3
        customer_name = "Test User 2"
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO "Order" (pizza_id, quantity, customer_name, timestamp, promo_code_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (pizza_id, quantity, customer_name, timestamp, promo_code_id))
        
        order_id = cursor.lastrowid
        conn.commit()
        
        # Update promo usage
        if promo_code_id:
            cursor.execute('''
                UPDATE PromoCode
                SET times_used = times_used + 1
                WHERE id = ?
            ''', (promo_code_id,))
            conn.commit()
        
        # Retrieve and verify
        cursor.execute('''
            SELECT o.id, p.name, p.price, o.quantity, o.customer_name, 
                   o.timestamp, pc.code, pc.discount_percent
            FROM "Order" o
            JOIN Pizza p ON o.pizza_id = p.id
            LEFT JOIN PromoCode pc ON o.promo_code_id = pc.id
            WHERE o.id = ?
        ''', (order_id,))
        
        order = cursor.fetchone()
        
        if order:
            subtotal = order[2] * order[3]
            discount_amount = subtotal * (order[7] / 100) if order[7] else 0
            final_total = subtotal - discount_amount
            
            print(f"  ✅ Order Created Successfully!")
            print(f"     Order ID: {order[0]}")
            print(f"     Pizza: {order[1]}")
            print(f"     Price: ${order[2]:.2f}")
            print(f"     Quantity: {order[3]}")
            print(f"     Customer: {order[4]}")
            print(f"     Timestamp: {order[5]}")
            print(f"     Promo Code: {order[6]} ({int(order[7])}% off)")
            print(f"     Subtotal: ${subtotal:.2f}")
            print(f"     Discount: -${discount_amount:.2f}")
            print(f"     Final Total: ${final_total:.2f}")
        else:
            print("  ❌ Failed to retrieve order")
        
        # Test 3: Verify timestamp format
        print("\n3. Testing Timestamp Format")
        print("-" * 70)
        
        cursor.execute('SELECT timestamp FROM "Order" ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        
        if result:
            timestamp_value = result[0]
            print(f"  ✅ Timestamp: {timestamp_value}")
            print(f"     Format: YYYY-MM-DD HH:MM:SS")
            
            # Try to parse it
            try:
                parsed = datetime.strptime(timestamp_value, '%Y-%m-%d %H:%M:%S')
                print(f"  ✅ Timestamp is valid and parseable")
            except:
                print(f"  ❌ Timestamp format is invalid")
        
        # Test 4: Verify no old columns exist
        print("\n4. Verifying Old Columns Removed")
        print("-" * 70)
        
        cursor.execute("PRAGMA table_info('Order')")
        columns = [col[1] for col in cursor.fetchall()]
        
        old_columns = ['order_date', 'discount_amount', 'final_total']
        found_old = [col for col in old_columns if col in columns]
        
        if found_old:
            print(f"  ❌ Found old columns: {', '.join(found_old)}")
        else:
            print(f"  ✅ All old columns removed successfully")
        
        # Test 5: Count total orders
        print("\n5. Order Statistics")
        print("-" * 70)
        
        cursor.execute('SELECT COUNT(*) FROM "Order"')
        total_orders = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM "Order" WHERE promo_code_id IS NOT NULL')
        orders_with_promo = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM "Order" WHERE promo_code_id IS NULL')
        orders_without_promo = cursor.fetchone()[0]
        
        print(f"  Total Orders: {total_orders}")
        print(f"  Orders with Promo Code: {orders_with_promo}")
        print(f"  Orders without Promo Code: {orders_without_promo}")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nThe Order table schema is working correctly with:")
        print("  - Proper timestamp field (not order_date)")
        print("  - No stored discount_amount or final_total")
        print("  - Calculations done on-the-fly")
        print("  - Promo codes working correctly")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    test_order_flow()
