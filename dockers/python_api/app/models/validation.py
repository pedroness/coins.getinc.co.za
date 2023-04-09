from pydantic import BaseModel,Extra,EmailStr,NameEmail,Field
from datetime import datetime, timedelta
from typing import List, Dict, Optional




# Pydantic models
class Login(BaseModel):
    username_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr
    scopes: list[str] = []


class RoleBase(BaseModel):
    name: str
    


class Role(RoleBase):
    id: int 
    permissions: Dict
    users: List["UserBase"] = []
    class Config:
        orm_mode = True

class Upload(BaseModel):
    id : int
    name : str
    path : str
    ext : str
    field_name : Optional[str] | None

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    
class UserUpdate(UserBase): 
    profile_upload_id: int
    disabled: bool 
    
class UserRead(UserUpdate):
    id: int
    role_id: int
    role: RoleBase
    profile_image: Upload 
    class Config:
        orm_mode = True
    
class UserCreate(UserBase):
    profile_upload_id: Optional[int] = 1
    password: str

    
class User(UserRead):
    password: str
   

       
class Response(BaseModel):
    status: str
    message: str

class TransferDetail(BaseModel): 
    description: str


class WalletBase(BaseModel):
    name : str
    available : int
    used : int

class Wallet(WalletBase):
    id : int
    user_id: int
    user: UserBase
    class Config:
        orm_mode = True



class ConfirmationRequestBase(BaseModel):
    confirmation_code: str
    email: EmailStr



class ConfirmationRequest(ConfirmationRequestBase): 
    id: int 
    confirmation_expiry_dt: datetime
    user: UserBase
    class Config:
        orm_mode = True



class PasswordResetRequestCreate(BaseModel):
    email:EmailStr
    password:str

class PasswordResetRequestRead(ConfirmationRequest):
    password:str

class EmailBase(BaseModel):
    email:EmailStr

ConfirmationRequest.update_forward_refs(user=UserBase)
Wallet.update_forward_refs(user=UserBase)
Role.update_forward_refs(users=UserBase)
User.update_forward_refs(role=RoleBase)
User.update_forward_refs(wallets=WalletBase)
