from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey,Date,DateTime,text,func,event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type

from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from sqlalchemy.ext.declarative import declarative_base
from models.seed import initialize_table

from config import env

env_var = env().env




# PY_DB_PORT=5432

password = env_var["PY_DB_PASSWORD"].replace("@", "%40" )

DATABASE_URL = "postgresql+psycopg2://"+env_var["PY_DB_USER"]+":"+password+"@"+env_var["PY_DB_HOST"]+"/"+env_var["PY_DB_DATABASE"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# SQLAlchemy models
class RoleDB(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    permissions = Column(JSONB, default=text("'{\"permissions\":[\"/\"]}'::jsonb"),server_default=text("'{\"permissions\":[\"/\"]}'::jsonb"))


class UploadDB(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    path = Column(String)
    ext = Column(String)
    field_name = Column(String)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, server_default='t', default=True)
    profile_upload_id = Column(Integer, ForeignKey("uploads.id"))
    profile_image = relationship("UploadDB", backref="users")
    create_dt = Column(DateTime, server_default=func.now())
    confirmation_requests = relationship("ConfirmationRequestDB", backref="user")
    # reset_requests = relationship('ResetRequestDB', backref='user', lazy=True)
    role_id = Column(Integer, ForeignKey('roles.id'), server_default=text("3"))
    role = relationship('RoleDB', backref='users')


class ConfirmationRequestDB(Base):
    __tablename__ = "confirmation_requests"
    id = Column(Integer, primary_key=True, index=True)
    confirmation_code = Column(String)
    email = Column(String)
    password = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    confirmation_expiry_dt	= Column(DateTime, server_default=text("(now() + interval '15 minutes')"))


class DateFuncDB(Base):
    __tablename__ = "time_functions"
    id = Column(Integer, primary_key=True, index=True)
    data = Column(String)
    func_current_date	= Column(DateTime, server_default=func.current_date())
    func_now = Column(DateTime, server_default=func.now())

class WalletDB(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    available = Column(Integer)
    used = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

class WalletHistoryDB(Base):
    __tablename__ = "wallet_history"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    description = Column(String)
    tags = Column(JSONB, default=text("'{\"tags\":[]}'::jsonb"),server_default=text("'{\"tags\":[]}'::jsonb"))
    user_id_from = Column(Integer)
    wallet_id_from = Column(Integer)
    user_id_to = Column(Integer)
    wallet_id_to = Column(Integer)
    created_dt	= Column(DateTime, server_default=func.current_date())
    
    
class ScreenTimeBookingDB(Base):
    __tablename__ = "screen_time_bookings"
    id = Column(Integer, primary_key=True, index=True)
    slot = Column(Integer)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    booking_dt = Column(Date)
    created_dt	= Column(DateTime, server_default=func.current_date())
  
# class ResetRequestDB(Base):
#     __tablename__ = "reset_requests"
#     id = Column(Integer, primary_key=True, index=True)
#     confirmation_code = Column(String)
#     email = Column(String, ForeignKey('users.email'), nullable=False)
#     password = Column(String)
#     requested_dt = Column(DateTime, server_default=func.now())

Session = sessionmaker(bind=engine)

# set up events before table creation
event.listen(RoleDB.__table__, 'after_create', initialize_table)
event.listen(UploadDB.__table__, 'after_create', initialize_table)
event.listen(UserDB.__table__, 'after_create', initialize_table)
event.listen(WalletDB.__table__, 'after_create', initialize_table)

Base.metadata.create_all(bind=engine)