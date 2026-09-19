from ..database.mongodb import products, utc_now

SEED_PRODUCTS = [
    ("Rice", "Grains", "kg", 25, 55, 10, 40), ("Wheat", "Grains", "kg", 8, 45, 10, 25),
    ("Sugar", "Staples", "kg", 5, 48, 10, 25), ("Cooking Oil", "Staples", "litre", 30, 120, 10, 35),
    ("Biscuits", "Snacks", "box", 18, 30, 8, 30), ("Milk", "Dairy", "litre", 12, 60, 5, 20),
    ("Tea", "Beverages", "piece", 22, 180, 8, 30), ("Soap", "Personal Care", "piece", 6, 35, 10, 25),
    ("Detergent", "Home Care", "kg", 14, 90, 6, 20), ("Coffee", "Beverages", "box", 9, 220, 5, 15),
]


def seed_database(owner_id):
    if products.count_documents({"owner_id": owner_id}) == 0:
        now = utc_now()
        products.insert_many([{"owner_id": owner_id, "name": name, "category": category, "unit": unit, "quantity": quantity, "price": price,
                               "low_stock_threshold": threshold, "target_stock": target, "created_at": now, "updated_at": now}
                              for name, category, unit, quantity, price, threshold, target in SEED_PRODUCTS])
