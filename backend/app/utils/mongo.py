from bson import ObjectId


def serialize_id(value):
    return str(value) if isinstance(value, ObjectId) else value


def owner_user(owner):
    store = owner.get("store", {})
    preferences = owner.get("preferences", {})
    return {"id": str(owner["_id"]), "full_name": owner["full_name"], "email": owner["email"], "phone": owner.get("phone", ""),
            "store_name": store.get("name", ""), "preferred_language": preferences.get("language", "en")}


def serialize_product(product):
    quantity = product.get("quantity", 0)
    threshold = product.get("low_stock_threshold", 10)
    status = "CRITICAL" if quantity <= threshold * 0.5 else "LOW" if quantity <= threshold else "HEALTHY"
    return {"id": str(product["_id"]), "name": product["name"], "category": product.get("category", "General"), "unit": product["unit"],
            "quantity": quantity, "price": product.get("price"), "low_stock_threshold": threshold, "target_stock": product.get("target_stock", 20),
            "created_at": product.get("created_at"), "updated_at": product.get("updated_at"), "status": status,
            "reorder_quantity": max(product.get("target_stock", 20) - quantity, 0)}


def serialize_transaction(item):
    return {"id": str(item["_id"]), "product_id": str(item["product_id"]), "product_name": item.get("product_name", ""),
            "transaction_type": item["transaction_type"], "quantity": item["quantity"], "unit": item["unit"], "price": item.get("price"),
            "source": item.get("source", "MANUAL"), "language": item.get("language"), "raw_text": item.get("raw_text"), "created_at": item.get("created_at")}
