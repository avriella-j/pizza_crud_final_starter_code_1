"""
Fix WELCOME10 promo code to have NULL usage_limit (unlimited)
"""
import sqlite3
import os

DB_PATH = os.path.join('data', 'pizzas.db')

print("=" * 70)
print("FIXING WELCOME10 PROMO CODE")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Check current state
    cursor.execute('SELECT id, code, usage_limit, times_used FROM PromoCode WHERE code = "WELCOME10"')
    result = cursor.fetchone()
    
    if result:
        promo_id, code, limit, used = result
        print(f"\nCurrent state:")
        print(f"  Code: {code}")
        print(f"  Usage Limit: {limit}")
        print(f"  Times Used: {used}")
        
        # Fix: Set usage_limit to NULL for unlimited
        cursor.execute('UPDATE PromoCode SET usage_limit = NULL WHERE code = "WELCOME10"')
        conn.commit()
        
        # Verify fix
        cursor.execute('SELECT id, code, usage_limit, times_used FROM PromoCode WHERE code = "WELCOME10"')
        result = cursor.fetchone()
        promo_id, code, limit, used = result
        
        print(f"\nFixed state:")
        print(f"  Code: {code}")
        print(f"  Usage Limit: {limit} (NULL = unlimited)")
        print(f"  Times Used: {used}")
        
        print("\n" + "=" * 70)
        print("✅ WELCOME10 fixed successfully!")
        print("=" * 70)
    else:
        print("❌ WELCOME10 not found in database")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
