from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import  Depends, HTTPException, status, Security,Request
from modules.auth import UserAuth,get_current_active_user,ACCESS_TOKEN_EXPIRE_MINUTES
from modules.documentation import route_doc
from models.db import UserDB,RoleDB,UploadDB, get_db
from models.validation import EmailBase, UserBase,User,UserUpdate,UserRead,UserCreate,Role,Token,Login,Response,PasswordResetRequestCreate

ua=UserAuth()

router = APIRouter(
    prefix="/users",
    tags=["User Profile Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me/", response_model=UserRead , tags=["User Profile Management"],description=route_doc("/users/me/"))
async def read_users_me (current_user: User = Security(get_current_active_user, scopes=["/users/me/"])): 
    print("reading current user")  
    print(current_user)
    return current_user

@router.post("/{user_id}/update/", response_model=Response , tags=["User Profile Management"],description=route_doc("/users/{user_id}/"))
async def update_user (user_id:int, user:UserUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["/users/{user_id}/"])): 
    
    return ua.update_user(user_id,user,db)
  
@router.post("/{user_id}/create/", response_model=Response , tags=["User Profile Management"],description=route_doc("/users/{user_id}/"))
async def create_user (user_id:int, user:UserCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["/users/{user_id}/"])): 
    
    return ua.create_user(user_id,user,db)

@router.get("/role/{role_id}/", response_model=Role,  tags=["User Profile Management"], description=route_doc("/users/role/{role_id}/"))
async def read_users_for_role_id (role_id = int,db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["/users/role/"])):   
    """
    Lists users in a given role

    """
    return ua.get_users_in_role(role_id,db)
