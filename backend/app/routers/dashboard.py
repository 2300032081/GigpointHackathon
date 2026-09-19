from fastapi import APIRouter, Depends
from ..database.mongodb import products, transactions
from ..dependencies.auth import get_current_owner
from ..utils.mongo import serialize_product

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/stats")
def stats(owner=Depends(get_current_owner)):
    items = list(products.find({"owner_id": str(owner["_id"])})); categories = sorted({p.get("category", "General") for p in items})
    return {"total_products": len(items), "total_stock_items": sum(p.get("quantity", 0) for p in items), "low_stock_items": sum(p.get("quantity", 0) <= p.get("low_stock_threshold", 10) for p in items), "critical_items": sum(p.get("quantity", 0) <= p.get("low_stock_threshold", 10) * 0.5 for p in items), "categories": [{"name": c, "value": sum(p.get("quantity", 0) for p in items if p.get("category") == c)} for c in categories]}

@router.get("/alerts")
def alerts(owner=Depends(get_current_owner)):
    return [serialize_product(p) for p in products.find({"owner_id": str(owner["_id"]), "$expr": {"$lte": ["$quantity", "$low_stock_threshold"]}})]

@router.get("/recent")
def recent(owner=Depends(get_current_owner)):
    return [{"product": t.get("product_name", ""), "type": t["transaction_type"], "quantity": t["quantity"], "unit": t["unit"], "created_at": t["created_at"]} for t in transactions.find({"owner_id": str(owner["_id"])}).sort("created_at", -1).limit(8)]
