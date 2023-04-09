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
    prefix="",
    tags=["User Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/token-form-access/", response_model=Token ,tags=["User Authentication"], description=route_doc("/token-form-access/"))
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Form based token authentication
    """
    # stuff to say ![This image works](https://upload.wikimedia.org/wikipedia/commons/0/08/STockholmspanorama_1928b.jpg)
    return ua.authenticate_user(form_data.username, form_data.password, db)
     

@router.post("/token/", response_model=Token,tags=["User Authentication"], description=route_doc("/token/"))
@router.post("/token", response_model=Token,tags=["User Authentication"], description=route_doc("/token/"))
async def token(form_data: Login, db: Session = Depends(get_db)):
    """
    Json body based token authentication
    """
    return ua.authenticate_user(form_data.username_or_email, form_data.password, db)


@router.post("/sign-up/",response_model=Response, tags=["User Authentication"], description=route_doc("/sign_up/"))
async def sign_up(user_in:UserCreate ,db: Session = Depends(get_db)):
    """
    User Sign Up 
    """
    db_user = ua.create_user(user_in,db)
    confirmation_code, confirmation_id = ua.create_confirmation_code(db_user,db)
    
    return ua.send_user_confirmation(confirmation_code, confirmation_id, db_user.email , db)

@router.post("/send-confirmation-mail/", tags=["User Authentication"], description=route_doc("/send_confirmation_mail/"))
async def send_confirmation_mail(user:EmailBase, db: Session = Depends(get_db)):
    """
    Re-generates sign_up confirmation email if not recieved
    """
    db_user=ua.get_user(user.email,db)
    confirmation_code, confirmation_id = ua.create_confirmation_code(db_user,db)
    return ua.send_user_confirmation(confirmation_code, confirmation_id, db_user.email , db)


@router.get("/check-confirmation-email/{confirmation_code}/{confirmation_id}/", response_model=Response,  tags=["User Authentication"], description=route_doc("/check-confirmation-email/{confirmation_code}/{confirmation_id}/"))
async def check_confirmation_email(confirmation_code:str,confirmation_id:int, db: Session = Depends(get_db)):   
    """
    Activates user account if the link is verified and the account is eligible for activation

    """
    return ua.confirm_confirmation_code(confirmation_id,confirmation_code,db)


@router.post("/create-reset-password/",response_model=Response,tags=["User Authentication"], description=route_doc("/create-reset-password/"))
async def create_reset_mail(userin:PasswordResetRequestCreate, db: Session = Depends(get_db)):
    """
    Generates a reset password email token confirmation
    """
    db_user=ua.get_user(userin.email,db)
    confirmation_code, confirmation_id = ua.create_user_reset_password_token(db_user,userin.password,db)
    return ua.send_user_password_reset_confirmation(confirmation_code, confirmation_id, db_user.email , db)

@router.get("/confirm-password-change/{confirmation_code}/{confirmation_id}/", response_model=Response,  tags=["User Authentication"], description=route_doc("/confirm-password-change/{confirmation_code}/{confirmation_id}/"))
async def check_confirmation_email(confirmation_code:str,confirmation_id:int, db: Session = Depends(get_db)):   
    """
    Activates user account if the link is verified and the account is eligible for activation

    """
    return ua.confirm_password_change(confirmation_id,confirmation_code,db) 
