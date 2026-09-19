from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError
from ..database.mongodb import owners, utc_now
from ..dependencies.auth import get_current_owner
from ..schemas.auth import AuthResponse, ProfileUpdate, SigninRequest, SignupRequest, UserResponse
from ..services.auth_service import create_access_token, hash_password, verify_password
from ..utils.mongo import owner_user
from ..utils.seed_data import seed_database

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/signup")
def signup(payload: SignupRequest):
    email = str(payload.email).lower(); now = utc_now()
    document = {"full_name": payload.full_name.strip(), "email": email, "phone": payload.phone, "password_hash": hash_password(payload.password), "store": {"name": payload.store_name, "business_type": payload.business_type, "phone": payload.store_phone, "address": payload.address, "city": payload.city, "state": payload.state, "pincode": payload.pincode, "gst_number": payload.gst_number, "description": payload.business_description}, "preferences": {"language": payload.preferred_language, "currency": payload.currency, "unit_system": payload.unit_system}, "is_active": True, "created_at": now, "updated_at": now}
    try:
        result = owners.insert_one(document)
        seed_database(str(result.inserted_id))
    except DuplicateKeyError: raise HTTPException(409, "An account with this email already exists")
    return {"success": True, "message": "Account created successfully. Please sign in."}

@router.post("/signin", response_model=AuthResponse)
def signin(payload: SigninRequest):
    owner = owners.find_one({"email": str(payload.email).lower()})
    if not owner or not verify_password(payload.password, owner.get("password_hash", "")): raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password.")
    return {"access_token": create_access_token(str(owner["_id"])), "token_type": "bearer", "user": owner_user(owner)}

@router.get("/me", response_model=UserResponse)
def me(owner=Depends(get_current_owner)):
    return owner_user(owner)

@router.put("/profile", response_model=UserResponse)
def update_profile(payload: ProfileUpdate, owner=Depends(get_current_owner)):
    values = payload.model_dump(); store = {"name": values.pop("store_name"), "business_type": values.pop("business_type"), "phone": values.pop("store_phone"), "address": values.pop("address"), "city": values.pop("city"), "state": values.pop("state"), "pincode": values.pop("pincode"), "gst_number": values.pop("gst_number"), "description": values.pop("business_description")}
    result = owners.find_one_and_update({"_id": owner["_id"]}, {"$set": {"full_name": values.pop("full_name"), "phone": values.pop("phone"), "store": store, "preferences": {"language": values.pop("preferred_language"), "currency": values.pop("currency"), "unit_system": values.pop("unit_system")}, "updated_at": utc_now()}}, return_document=ReturnDocument.AFTER)
    return owner_user(result)

@router.post("/logout")
def logout(owner=Depends(get_current_owner)):
    return {"success": True, "message": "Logged out"}
