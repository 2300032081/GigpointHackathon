from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class SignupRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str
    password: str = Field(min_length=8)
    store_name: str = Field(min_length=1, max_length=120)
    business_type: str = Field(min_length=1, max_length=80)
    store_phone: str
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str
    preferred_language: str = "en"
    currency: str = "INR"
    unit_system: str = "Indian Trade Units"
    gst_number: Optional[str] = None
    business_description: str = ""

    @field_validator("phone", "store_phone")
    @classmethod
    def valid_phone(cls, value):
        if not value.isdigit() or len(value) != 10 or value[0] not in "6789":
            raise ValueError("Enter a valid 10-digit Indian mobile number")
        return value

    @field_validator("pincode")
    @classmethod
    def valid_pincode(cls, value):
        if not value.isdigit() or len(value) != 6:
            raise ValueError("PIN code must contain exactly 6 digits")
        return value

    @field_validator("password")
    @classmethod
    def strong_password(cls, value):
        if not any(c.isupper() for c in value) or not any(c.islower() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password needs uppercase, lowercase, and a number")
        return value

class SigninRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=120)
    phone: str
    store_name: str = Field(min_length=1, max_length=120)
    business_type: str
    store_phone: str
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str
    preferred_language: str = "en"
    currency: str = "INR"
    unit_system: str = "Indian Trade Units"
    gst_number: Optional[str] = None
    business_description: str = ""

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: str
    store_name: str
    preferred_language: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
