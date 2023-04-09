from fastapi.security import  OAuth2PasswordRequestForm,OAuth2PasswordBearer,SecurityScopes
from fastapi import Depends, HTTPException, status
from pydantic import parse_obj_as
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from passlib.context import CryptContext
from models.db import ScreenTimeBookingDB,WalletHistoryDB,UserDB,RoleDB,UploadDB,WalletDB,DateFuncDB,get_db,engine
from models.validation import WalletBase,User,UserBase,UserCreate,UserUpdate,RoleBase, Role, TokenData, Token
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_, func
from typing import List
from modules.send_email import sm
import uuid
from config import env
import math


class Wallet():
    def __init__(self):
        con=engine.connect() 
        pass

    
    def get_wallet_info(self,user_id:int,db: Session=Depends(get_db)): 
        wallet = db.query(WalletDB).filter(WalletDB.user_id==user_id).first()
        walletdict = wallet.__dict__
        del walletdict['_sa_instance_state']
        del walletdict['user_id']
        walletdict['wallet_id']=walletdict['id']
        del walletdict['id']
        # del walletdict['id']
        slots=math.floor(walletdict['available']/30000)
        if slots>0:
            walletdict['message']="Congratulations you are able to book "+str(slots)+" slots"     
        return walletdict
    
    def pay_wallet(self,user,to_wallet_id,description,amount,db: Session=Depends(get_db)): 
        from_wallets = db.query(WalletDB).filter(WalletDB.user_id==user['id']).first()
        from_wallets.id
        from_wallets.user_id
        from_wallets.available
     
        if amount>from_wallets.available:
            raise HTTPException(
                status_code=200,
                detail="You don't have enough xp to transfer",
                
                )
        
        to_wallet=db.query(WalletDB).get(to_wallet_id)

        if to_wallet:
            to_wallet.available=to_wallet.available+amount
            from_wallets.available=from_wallets.available-amount
            db_transaction_history = WalletHistoryDB(amount=amount,description=description,
                                            user_id_from=from_wallets.user_id,
                                            wallet_id_from=from_wallets.id,
                                            user_id_to=to_wallet.user_id,
                                            wallet_id_to=to_wallet.id)

            db.add(db_transaction_history)
            db.add(from_wallets)
            db.add(to_wallet)
            db.commit()
            db.refresh(db_transaction_history)
            db.refresh(from_wallets)
            db.refresh(to_wallet)
        else:
            raise HTTPException(
                status_code=401,
                detail="No such wallet exists",
                
                )
        return {"message":"XP Sent"}
    def book_screen_time(self,user,date,description,slot,db: Session=Depends(get_db)):

        today = date.today()
        month_end=today + relativedelta(months=2)
        if slot > 4 or slot < 1:
            return {"message":"There are only 4 slots per day please select from 1 to 4"}
        if date < today or date > month_end:
            return {"message":"Your can only make bookings within the next 2 month "}
   
        wallet = db.query(WalletDB).filter(WalletDB.user_id==user['id']).first()
        slots=math.floor(wallet.available/30000)
        if slots<1:
            return {"message":"You don't have enough XP to book a slot"}
             
        screen_times = db.query(ScreenTimeBookingDB).filter(ScreenTimeBookingDB.booking_dt==date).all()
        
        if len(screen_times)>4:
            return {"message":"Slots for "+str(date)+" have already been full, please select another date"}
        
            
        slotexists = db.query(ScreenTimeBookingDB).filter(and_(ScreenTimeBookingDB.booking_dt==date,ScreenTimeBookingDB.slot==slot)).first()
        if slotexists:
            return {"message":"Slot "+str(slot)+" has already been booked, please select another slot"}



        new_booking=ScreenTimeBookingDB(slot=slot,description=description,user_id=user['id'],booking_dt=date)
        wallet.available=wallet.available-30000
        wallet.used=wallet.used+30000

        db.add(wallet)
        db.add(new_booking)
        db.commit()

        return {"message":"Awesome "+user['username']+", Your slot has been booked for "+str(date)}
    
    




