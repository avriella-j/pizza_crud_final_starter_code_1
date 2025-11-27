import sqlite3
import os

DB_PATH = os.path.join('data', 'pizzas.db')

def migrate_database():
    """Migrate the Order table to new schema"""
    print("Starting database migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if old Order table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Order'")
        if cursor.fetchone():
            print("Found existing Order table. Backing up data...")
            
            # Create backup of old data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Order_backup AS 
                SELECT * FROM "Order"
            ''')
            
            # Drop old Order table
            cursor.execute('DROP TABLE "Order"')
            print("Dropped old Order table")
        
        # Create new Order table with simplified schema
        cursor.execute('''
            CREATE TABLE "Order" (
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
        print("Created new Order table with simplified schema")
        
        # Migrate data from backup if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Order_backup'")
        if cursor.fetchone():
            print("Migrating data from backup...")
            cursor.execute('''
                INSERT INTO "Order" (id, pizza_id, quantity, customer_name, timestamp, promo_code_id)
                SELECT id, pizza_id, quantity, customer_name, 
                       COALESCE(order_date, datetime('now')), promo_code_id
                FROM Order_backup
            ''')
            print(f"Migrated {cursor.rowcount} orders")
            
            # Drop backup table
            cursor.execute('DROP TABLE Order_backup')
            print("Dropped backup table")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        migrate_database()
    else:
        print("No database found. Run the app to create a new database with the correct schema.")
