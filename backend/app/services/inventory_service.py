from fastapi import HTTPException
from pymongo import ReturnDocument
from ..database.mongodb import products, transactions, utc_now
from ..schemas.product import ProductCreate, ProductUpdate
from ..schemas.transaction import TransactionCreate
from ..utils.units import normalize_unit


def create_product(owner_id, payload: ProductCreate):
    unit = normalize_unit(payload.unit); name = payload.name.strip()
    if not unit: raise HTTPException(400, "Unit is required")
    if products.find_one({"owner_id": owner_id, "name": {"$regex": f"^{name}$", "$options": "i"}}): raise HTTPException(409, "A product with this name already exists")
    now = utc_now(); document = {**payload.model_dump(), "owner_id": owner_id, "name": name, "unit": unit, "created_at": now, "updated_at": now}
    document["_id"] = products.insert_one(document).inserted_id
    return document


def update_product(owner_id, product_id, payload: ProductUpdate):
    values = payload.model_dump(); values["name"] = values["name"].strip(); values["unit"] = normalize_unit(values["unit"]); values["updated_at"] = utc_now()
    result = products.find_one_and_update({"_id": product_id, "owner_id": owner_id}, {"$set": values}, return_document=ReturnDocument.AFTER)
    if not result: raise HTTPException(404, "Product not found")
    return result


def apply_transaction(owner_id, product_id, payload: TransactionCreate, transaction_type: str):
    product = products.find_one({"_id": product_id, "owner_id": owner_id})
    if not product: raise HTTPException(404, "Product not found")
    if transaction_type == "OUT" and payload.quantity > product.get("quantity", 0): raise HTTPException(400, f"Insufficient stock. Only {product.get('quantity', 0):g} {product['unit']} is available.")
    update = {"$inc": {"quantity": payload.quantity if transaction_type == "IN" else -payload.quantity}, "$set": {"updated_at": utc_now()}}
    if payload.price is not None: update["$set"]["price"] = payload.price
    query = {"_id": product_id, "owner_id": owner_id}
    if transaction_type == "OUT": query["quantity"] = {"$gte": payload.quantity}
    updated = products.find_one_and_update(query, update, return_document=ReturnDocument.AFTER)
    if not updated: raise HTTPException(400, "Insufficient stock")
    transaction = {"owner_id": owner_id, "product_id": product_id, "product_name": updated["name"], "transaction_type": transaction_type, "quantity": payload.quantity, "unit": normalize_unit(payload.unit or updated["unit"]) or updated["unit"], "price": payload.price, "source": payload.source.upper(), "language": payload.language, "raw_text": payload.raw_text, "created_at": utc_now()}
    transaction["_id"] = transactions.insert_one(transaction).inserted_id
    return transaction
