from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from ..database.mongodb import transactions
from ..dependencies.auth import get_current_owner
from ..schemas.transaction import TransactionCreate, TransactionResponse
from ..services.inventory_service import apply_transaction
from ..utils.mongo import serialize_transaction

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post("/{direction}", response_model=TransactionResponse, status_code=201)
def stock_change(direction: str, payload: TransactionCreate, owner=Depends(get_current_owner)):
    if direction not in {"in", "out"} or not ObjectId.is_valid(str(payload.product_id)): raise HTTPException(400, "Invalid transaction request")
    return serialize_transaction(apply_transaction(str(owner["_id"]), ObjectId(str(payload.product_id)), payload, direction.upper()))

@router.get("", response_model=list[TransactionResponse])
def list_transactions(transaction_type: str | None = None, owner=Depends(get_current_owner)):
    query = {"owner_id": str(owner["_id"])}
    if transaction_type: query["transaction_type"] = transaction_type.upper()
    return [serialize_transaction(item) for item in transactions.find(query).sort("created_at", -1).limit(50)]
