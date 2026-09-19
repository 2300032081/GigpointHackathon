from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from ..database.mongodb import products
from ..dependencies.auth import get_current_owner
from ..schemas.product import ProductCreate, ProductResponse, ProductUpdate
from ..services.inventory_service import create_product, update_product
from ..utils.mongo import serialize_product

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("", response_model=list[ProductResponse])
def list_products(search: str | None = None, category: str | None = None, owner=Depends(get_current_owner)):
    query = {"owner_id": str(owner["_id"])}
    if search: query["name"] = {"$regex": search, "$options": "i"}
    if category: query["category"] = category
    return [serialize_product(item) for item in products.find(query).sort("name", 1)]

@router.post("", response_model=ProductResponse, status_code=201)
def add_product(payload: ProductCreate, owner=Depends(get_current_owner)):
    return serialize_product(create_product(str(owner["_id"]), payload))

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, owner=Depends(get_current_owner)):
    if not ObjectId.is_valid(product_id): raise HTTPException(404, "Product not found")
    item = products.find_one({"_id": ObjectId(product_id), "owner_id": str(owner["_id"])})
    if not item: raise HTTPException(404, "Product not found")
    return serialize_product(item)

@router.put("/{product_id}", response_model=ProductResponse)
def edit_product(product_id: str, payload: ProductUpdate, owner=Depends(get_current_owner)):
    if not ObjectId.is_valid(product_id): raise HTTPException(404, "Product not found")
    return serialize_product(update_product(str(owner["_id"]), ObjectId(product_id), payload))

@router.delete("/{product_id}")
def delete_product(product_id: str, owner=Depends(get_current_owner)):
    if not ObjectId.is_valid(product_id): raise HTTPException(404, "Product not found")
    result = products.delete_one({"_id": ObjectId(product_id), "owner_id": str(owner["_id"])})
    if result.deleted_count == 0: raise HTTPException(404, "Product not found")
    return {"success": True}
