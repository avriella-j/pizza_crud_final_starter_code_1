import sqlite3

# Connect to the database
conn = sqlite3.connect('data/pizzas.db')
cursor = conn.cursor()

print("=" * 70)
print("PROMO CODES")
print("=" * 70)

# Check if PromoCode table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='PromoCode'")
if not cursor.fetchone():
    print("\n⚠️  PromoCode table does not exist yet.")
    print("Run the app first to create the table: python run.py")
else:
    # Show PromoCode table structure
    cursor.execute("PRAGMA table_info(PromoCode)")
    columns = cursor.fetchall()
    print("\nTable Structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Show all promo codes
    cursor.execute('''
        SELECT id, code, discount_percent, start_date, end_date, usage_limit, times_used
        FROM PromoCode
        ORDER BY id
    ''')
    promo_codes = cursor.fetchall()
    
    print(f"\nTotal Promo Codes: {len(promo_codes)}")
    print("\nPromo Code Details:")
    print("-" * 70)
    
    for promo in promo_codes:
        promo_id, code, discount, start, end, limit, used = promo
        
        print(f"\n📌 {code}")
        print(f"   ID: {promo_id}")
        print(f"   Discount: {discount}%")
        print(f"   Start Date: {start if start else 'No restriction'}")
        print(f"   End Date: {end if end else 'No restriction'}")
        
        if limit == -1:
            print(f"   Usage Limit: Unlimited")
            print(f"   Times Used: {used}")
        else:
            remaining = limit - used
            print(f"   Usage Limit: {limit}")
            print(f"   Times Used: {used}")
            print(f"   Remaining: {remaining}")
            
            if remaining == 0:
                print(f"   ⚠️  STATUS: EXHAUSTED")
            elif remaining < 10:
                print(f"   ⚠️  STATUS: Low availability")
            else:
                print(f"   ✅ STATUS: Available")

conn.close()
print("\n" + "=" * 70)
