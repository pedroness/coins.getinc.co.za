from fastapi.security import  OAuth2PasswordRequestForm,OAuth2PasswordBearer,SecurityScopes
from fastapi import Depends, HTTPException, status
from pydantic import parse_obj_as
from datetime import datetime, timedelta
from passlib.context import CryptContext
from models.db import UserDB,RoleDB,UploadDB,ConfirmationRequestDB,DateFuncDB,get_db,engine
from models.validation import User,UserBase,UserCreate,UserUpdate,RoleBase, Role, TokenData, Token
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, func
from typing import List
from modules.send_email import sm
import uuid
from config import env

env_var = env().env

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 525600

def set_scopes():
    scopes={}
    db=engine.connect()
    roles = db.execute(text("SELECT * FROM roles"))
    for role in roles:
        for route in role.permissions['routes']: 
            if route not in scopes.keys():
                scopes[route] ="User Access: "+role.name
            else:
                scopes[route]=scopes[route]+" / "+role.name
    return scopes

def create_access_token( data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token-form-access",                                  
scopes=set_scopes(),)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



async def get_current_user(security_scopes: SecurityScopes, db: Session=Depends(get_db), token: str = Depends(oauth2_scheme)):

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Could not validate credentials",
                        headers={"WWW-Authenticate": authenticate_value},)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, email=email)

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    user = db.query(UserDB).filter(UserDB.email == token_data.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    for scope in security_scopes.scopes:
        if scope not in user.role.permissions['routes'] or scope not in token_data.scopes:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your user is logged in as ("+user.role.name+") and does not have permisions for this route - "+",".join(security_scopes.scopes),
            headers={"WWW-Authenticate": authenticate_value},)

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    else:
        new_user=current_user.__dict__
        new_user['role']=current_user.role.__dict__
        new_user['profile_image']=current_user.profile_image.__dict__
    return new_user



class UserAuth():
    def __init__(self):
        con=engine.connect() 
        pass
    def verify_password(self,plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self,password):
        return pwd_context.hash(password)

    def get_user(self,  username_or_email: str, db: Session=Depends(get_db)):
        user = db.query(UserDB).filter(or_(UserDB.email == username_or_email,UserDB.username == username_or_email)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No such user found")
        return user    
    


    def authenticate_user(self,  username_or_email: str, password: str, db: Session=Depends(get_db)):
        user = db.query(UserDB).filter(or_(UserDB.email == username_or_email,UserDB.username == username_or_email)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No such user found")

        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
      
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email,"scopes":user.role.permissions['routes'] },
            expires_delta=access_token_expires, 
                
        )
        return Token(**{"access_token": access_token, "token_type": "bearer"})
    





    def create_user(self,user:UserCreate,db: Session=Depends(get_db)): 
        user_data = user.dict()
        user_data.pop("password")
        user_data['hashed_password'] = self.get_password_hash(user.password)
        db_user = UserDB(**user_data)
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        
        except Exception as e:  
            raise HTTPException(
            status_code=401,
            detail="That username or email already exists, please signin or select another",
            headers={"WWW-Authenticate": "Bearer"},
            )
        else:    
            return db_user
    def confirm_confirmation_code(self,confirmation_id:int,confirmation_code:str,db: Session=Depends(get_db)): 

        db_confirmation = db.query(ConfirmationRequestDB).filter(and_(ConfirmationRequestDB.id==confirmation_id,
                          ConfirmationRequestDB.confirmation_code==confirmation_code)).first()

        db_dt = DateFuncDB(data=db_confirmation.email)
        db.add(db_dt)
        db.commit()
        db.refresh(db_dt)

        if db_dt.func_now <= db_confirmation.confirmation_expiry_dt:            
            if db_confirmation.user.disabled==False:
                raise HTTPException(
                status_code=403,
                detail="This user has already been activated",
                
                )
            db_confirmation.user.disabled=False
            db.add(db_confirmation)
            db.commit()
            db.refresh(db_confirmation)

            db.delete(db_dt)
            db.commit()
        else:
            raise HTTPException(
            status_code=403,
             detail="This confirmation code has expired",
                
            )
        return {"status":"activated","message":"Please log on to use your account"}
    
    def confirm_password_change(self,confirmation_id:int,confirmation_code:str,db: Session=Depends(get_db)): 

        db_confirmation = db.query(ConfirmationRequestDB).filter(and_(ConfirmationRequestDB.id==confirmation_id,
                          ConfirmationRequestDB.confirmation_code==confirmation_code)).first()

        db_dt = DateFuncDB(data=db_confirmation.email)
        db.add(db_dt)
        db.commit()
        db.refresh(db_dt)

        if db_dt.func_now <= db_confirmation.confirmation_expiry_dt:            
            if db_confirmation.user.disabled==True:
                raise HTTPException(
                status_code=403,
                detail="This user is disabled and cannot change their password",
                
                )
            
            db_confirmation.user.hashed_password=db_confirmation.password
            db.add(db_confirmation)
            db.commit()
            db.refresh(db_confirmation)

            db.delete(db_dt)
            db.commit()
        else:
            raise HTTPException(
            status_code=403,
             detail="This reset token has expired",
                
            )
        return {"status":"activated","message":"Please log on to use your account"}





        # print(db_confirmation.id,db_confirmation.confirmation_code,db_confirmation.confirmation_expiry_dt,db_dt.func_now)

    def create_confirmation_code(self,db_user, db: Session=Depends(get_db)):
        if db_user.disabled == False:
            raise HTTPException(
            status_code=403,
            detail="You do not meet confirmation email criteria, please contact support",
        )
        todays_confirmations = db.query(ConfirmationRequestDB).filter(and_(ConfirmationRequestDB.user_id == db_user.id,func.date(ConfirmationRequestDB.confirmation_expiry_dt) == func.current_date(),ConfirmationRequestDB.password.is_(None))).all()
       
        print("confirmations",len(todays_confirmations),todays_confirmations)
        if len(todays_confirmations)>4:
            raise HTTPException(
            status_code=403,
            detail="Your maximum daily confirmation requests have been reached",
            )        

        db_confirmation = ConfirmationRequestDB(confirmation_code=str(uuid.uuid4()), email=db_user.email, user_id=db_user.id)
        db.add(db_confirmation)
        db.commit()
        db.refresh(db_confirmation)
        return db_confirmation.confirmation_code, db_confirmation.id
    
    def send_user_confirmation(self, confirmation_code, confirmation_id, email,db):
        send = sm(email, "Verify Your Email")
        send.buildmail(
            "<div><a href=\""+ env_var["PY_WEB_HOST"]+ "/check-confirmation-email/"
            + confirmation_code
            + "/"
            + str(confirmation_id)
            + "\">"
            + env_var["PY_WEB_HOST"]
            + "/check-confirmation-email/"
            + confirmation_code
            + "/"
            + str(confirmation_id)
            + "</a></div>"     
        )
        send.send()
        return {"status":"sent", "message":"Email confirmation has been sent."}

    def create_user_reset_password_token(self,db_user, password, db: Session=Depends(get_db)):
        if db_user.disabled == True:
            raise HTTPException(
            status_code=403,
            detail="You may not change the your account password as your account is disabled",
        )
        # ,
        todays_confirmations = db.query(ConfirmationRequestDB).filter(and_(ConfirmationRequestDB.user_id == db_user.id,func.date(ConfirmationRequestDB.confirmation_expiry_dt) == func.current_date(),ConfirmationRequestDB.password.is_not(None))).all()
        
        print("Confirmations:",len(todays_confirmations),todays_confirmations)
        if len(todays_confirmations)>4:
            raise HTTPException(
            status_code=403,
            detail="Your maximum daily password resets have been reached",
            )        

        db_confirmation = ConfirmationRequestDB(confirmation_code=str(uuid.uuid4()), email=db_user.email, user_id=db_user.id, password=self.get_password_hash(password))
        db.add(db_confirmation)
        db.commit()
        db.refresh(db_confirmation)
        return db_confirmation.confirmation_code, db_confirmation.id

    def send_user_password_reset_confirmation(self, confirmation_code, confirmation_id, email,db):
        send = sm(email, "Confirm Password Change ")
        send.buildmail(
            "<div><a href=\""+ env_var["PY_WEB_HOST"]+ "/confirm-password-change/"
            + confirmation_code
            + "/"
            + str(confirmation_id)
            + "\">"
            + env_var["PY_WEB_HOST"]
            + "/confirm-password-change/"
            + confirmation_code
            + "/"
            + str(confirmation_id)
            + "</a></div>"     
        )
        send.send()
        return {"status":"sent", "message":"Password Change Email confirmation has been sent."}

       
   

        


    def get_users_in_role(self,role_id, db: Session=Depends(get_db)):
        dbrole = db.query(RoleDB).filter(RoleDB.id == role_id).first()
        role=parse_obj_as(Role, dbrole.__dict__)
        for user in dbrole.users:
            user_dict=user.__dict__
            role.users.append(parse_obj_as(UserBase, user_dict))
        return role





