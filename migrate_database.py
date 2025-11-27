import sqlite3
import os

DB_PATH = os.path.join('data', 'pizzas.db')

print("=" * 70)
print("DATABASE MIGRATION - Adding Promo Code Support")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check current Order table structure
    cursor.execute("PRAGMA table_info('Order')")
    columns = cursor.fetchall()
    existing_columns = [col[1] for col in columns]
    
    print("\nCurrent Order table columns:")
    for col in existing_columns:
        print(f"  - {col}")
    
    # Add missing columns if they don't exist
    columns_to_add = [
        ('promo_code_id', 'INTEGER'),
        ('discount_amount', 'REAL DEFAULT 0'),
        ('final_total', 'REAL')
    ]
    
    print("\nAdding missing columns...")
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE "Order" ADD COLUMN {col_name} {col_type}')
                print(f"  ✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Column {col_name} might already exist: {e}")
        else:
            print(f"  ℹ️  Column {col_name} already exists")
    
    # Update existing orders to have final_total = subtotal (for orders without promo codes)
    print("\nUpdating existing orders...")
    cursor.execute('''
        UPDATE "Order"
        SET final_total = (
            SELECT p.price * "Order".quantity
            FROM Pizza p
            WHERE p.id = "Order".pizza_id
        )
        WHERE final_total IS NULL
    ''')
    rows_updated = cursor.rowcount
    print(f"  ✅ Updated {rows_updated} existing orders with final_total")
    
    conn.commit()
    
    # Verify the changes
    print("\nVerifying changes...")
    cursor.execute("PRAGMA table_info('Order')")
    columns = cursor.fetchall()
    print("\nUpdated Order table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    print("\n" + "=" * 70)
    print("✅ Migration completed successfully!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    conn.rollback()
    raise
finally:
    conn.close()
