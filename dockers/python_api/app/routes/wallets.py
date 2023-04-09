from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, func
from fastapi import APIRouter
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import  Depends, HTTPException, status, Security,Request
from modules.auth import UserAuth,get_current_active_user,ACCESS_TOKEN_EXPIRE_MINUTES
from modules.documentation import route_doc
from modules.wallets import Wallet
from models.db import ScreenTimeBookingDB,UserDB,RoleDB,UploadDB, get_db
from models.validation import TransferDetail,WalletBase,EmailBase, User,UserUpdate,UserRead,UserCreate,Role,Token,Login,Response,PasswordResetRequestCreate
from pydantic import parse_obj_as
from datetime import date,datetime,timedelta

w=Wallet()

router = APIRouter(
    prefix="/wallets",
    tags=["Wallet Management"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me/",description=route_doc("/wallets/me/"))
async def read_wallet_me (db: Session = Depends(get_db),  current_user: User = Security(get_current_active_user, scopes=["/wallets/me/"])): 
    
    
    todaybookings = db.query(ScreenTimeBookingDB).filter(and_(ScreenTimeBookingDB.booking_dt==date.today(),ScreenTimeBookingDB.user_id==current_user['id'])).all()
    futurebookings = db.query(ScreenTimeBookingDB).filter(and_(ScreenTimeBookingDB.booking_dt>date.today(),ScreenTimeBookingDB.user_id==current_user['id'])).all()
    
    
    return {"user_id":current_user['id'],"username":current_user['username'],
             "wallet_info":w.get_wallet_info(current_user['id'],db),
             "todays_bookings":todaybookings,"future_bookings":futurebookings}

@router.post("/transfer/xp/{amount}/to/{wallet_id}/{description}", description=route_doc("/wallets/me/"))
async def transfer_wallet_xp (wallet_id:int,description:str, amount:int,  db: Session = Depends(get_db),  from_user: User = Security(get_current_active_user, scopes=["/wallets/me/"])): 
    return w.pay_wallet(from_user,wallet_id,description,amount,db)


@router.post("/book-screen-time/{slot}/{bookdate}/{description}/", description=route_doc("/wallets/me/"))
async def transfer_wallet_xp (slot:int,bookdate:date,description:str,  db: Session = Depends(get_db),  user: User = Security(get_current_active_user, scopes=["/wallets/me/"])): 
    return w.book_screen_time(user,bookdate,description,slot,db)


@router.get("/view-bookings/today/", description=route_doc("/wallets/me/"))
async def view_bookings (db: Session = Depends(get_db),  user: User = Security(get_current_active_user, scopes=["/wallets/me/"])): 
    
    screenbookings=db.query(ScreenTimeBookingDB).filter(ScreenTimeBookingDB.booking_dt==date.today()).all()

    
    return screenbookings

@router.get("/view-bookings/", description=route_doc("/wallets/me/"))
async def view_bookings (db: Session = Depends(get_db),  user: User = Security(get_current_active_user, scopes=["/wallets/me/"])): 
    
    screenbookings=db.query(ScreenTimeBookingDB).filter(ScreenTimeBookingDB.booking_dt>=date.today()).all()

    
    return screenbookings



