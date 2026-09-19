from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from ..database.mongodb import assistant_logs, products, utc_now
from ..dependencies.auth import get_current_owner
from ..schemas.assistant import ParseResponse, TextRequest
from ..services.nlp_service import parse_text

router = APIRouter(prefix="/api", tags=["assistant"])

@router.post("/nlp/parse", response_model=ParseResponse)
def parse_command(payload: TextRequest, owner=Depends(get_current_owner)):
    return parse_text(str(owner["_id"]), payload.text, payload.language)

@router.post("/assistant/process", response_model=ParseResponse)
def process_command(payload: TextRequest, owner=Depends(get_current_owner)):
    parsed = parse_text(str(owner["_id"]), payload.text, payload.language)
    if parsed["intent"] in {"ADD_STOCK", "REMOVE_STOCK"} and (not parsed["product_id"] or not parsed["quantity"]): raise HTTPException(422, "Please include a product and quantity")
    return parsed

@router.post("/assistant/query")
def query_assistant(payload: TextRequest, owner=Depends(get_current_owner)):
    owner_id = str(owner["_id"]); parsed = parse_text(owner_id, payload.text, payload.language); items = list(products.find({"owner_id": owner_id})); product = products.find_one({"_id": ObjectId(parsed["product_id"]), "owner_id": owner_id}) if parsed["product_id"] else None
    if parsed["intent"] == "CHECK_STOCK": response = f"You currently have {product['quantity']:g} {product['unit']} of {product['name']}." if product else "Please mention a product to check its stock."
    elif parsed["intent"] == "LOW_STOCK": response = "Low stock: " + (", ".join(p["name"] for p in items if p.get("quantity", 0) <= p.get("low_stock_threshold", 10)) or "Nothing right now.")
    elif parsed["intent"] == "REORDER": response = "Smart reorder suggestions: " + ("; ".join(f"{p['name']}: order {max(p.get('target_stock', 20)-p.get('quantity', 0), 0):g} {p['unit']}" for p in items if p.get("quantity", 0) <= p.get("low_stock_threshold", 10)) or "No reorder needed.")
    elif parsed["intent"] == "LIST_PRODUCTS": response = "Inventory: " + ", ".join(f"{p['name']} ({p.get('quantity', 0):g} {p['unit']})" for p in items)
    else: response = "I can check stock, show low-stock items, suggest reorders, or list your inventory."
    assistant_logs.insert_one({"owner_id": owner_id, "question": payload.text, "intent": parsed["intent"], "response": response, "language": parsed["language"], "created_at": utc_now()})
    return {**parsed, "response": response}
