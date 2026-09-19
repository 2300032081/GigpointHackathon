import re
from difflib import SequenceMatcher
from ..database.mongodb import products
from ..utils.units import normalize_unit

ALIASES = {"rice": {"rice", "chawal", "biyyam", "biyyam rice"}, "sugar": {"sugar", "cheeni", "chini"}, "wheat": {"wheat", "gehun", "godhuma"}, "cooking oil": {"oil", "cooking oil", "tel", "nune"}, "milk": {"milk", "doodh", "paalu"}, "biscuits": {"biscuit", "biscuits"}}
ADD_WORDS = {"add", "adding", "received", "receive", "bought", "came", "aayi", "vachindi", "cheyyi", "mein"}
OUT_WORDS = {"sold", "sell", "remove", "removed", "bech", "bechna", "bechdiya", "nikal", "went"}


def detect_language(text: str, requested: str | None = None) -> str:
    if requested: return requested.split("-")[0].lower()
    if re.search(r"[\u0900-\u097F]", text): return "hi"
    if re.search(r"[\u0C00-\u0C7F]", text): return "te"
    if any(word in text.lower().split() for word in {"karo", "kitna", "chawal", "cheeni", "hai", "biyyam", "add", "stock"}): return "mixed"
    return "en"


def _find_product(text: str, owner_id: str):
    normalized = text.lower(); best, score = None, 0.0
    for product in products.find({"owner_id": owner_id}):
        for name in {product["name"].lower()} | ALIASES.get(product["name"].lower(), set()):
            current = 1.0 if name in normalized else SequenceMatcher(None, name, normalized).ratio() * 0.8
            if current > score: best, score = product, current
    return best


def parse_text(owner_id: str, text: str, language: str | None = None):
    lowered = text.lower(); product = _find_product(text, owner_id)
    quantity_match = re.search(r"(?:^|\s)(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilo|kilos|g|gram|grams|bag|bags|box|boxes|carton|cartons|litre|litres|liter|liters|piece|pieces|pc|pcs|dozen|dozens|quintal|quintals)?", lowered)
    quantity = float(quantity_match.group(1)) if quantity_match else None
    unit_match = re.search(r"\b(kg|kgs|kilo|kilos|g|gram|grams|bag|bags|box|boxes|carton|cartons|litre|litres|liter|liters|piece|pieces|pc|pcs|dozen|dozens|quintal|quintals)\b", lowered)
    unit = normalize_unit(unit_match.group(1)) if unit_match else (product.get("unit") if product else None)
    price_match = re.search(r"(?:at|price|rupees?|rs\.?)\s*(?:is\s*)?(\d+(?:\.\d+)?)", lowered)
    price = float(price_match.group(1)) if price_match else None; tokens = set(re.findall(r"[a-z]+", lowered))
    if any(word in lowered for word in {"how much", "kitna", "stock", "available", "bacha"}): intent = "CHECK_STOCK"
    elif "low" in lowered or "kam" in lowered or "running out" in lowered: intent = "LOW_STOCK"
    elif any(word in lowered for word in {"reorder", "order", "buy", "purchase"}): intent = "REORDER"
    elif any(word in lowered for word in {"show all", "inventory", "products", "items"}): intent = "LIST_PRODUCTS"
    elif tokens & OUT_WORDS: intent = "REMOVE_STOCK"
    elif tokens & ADD_WORDS or quantity is not None: intent = "ADD_STOCK"
    else: intent = "UNKNOWN"
    transaction_type = "IN" if intent == "ADD_STOCK" else "OUT" if intent == "REMOVE_STOCK" else None
    confidence = min(0.99, 0.62 + (0.22 if product else 0) + (0.1 if quantity is not None else 0) + (0.05 if intent != "UNKNOWN" else 0))
    return {"success": True, "intent": intent, "product": product["name"] if product else None, "product_id": str(product["_id"]) if product else None, "quantity": quantity, "unit": unit, "price": price, "transaction_type": transaction_type, "language": detect_language(text, language), "confidence": round(confidence, 2)}
