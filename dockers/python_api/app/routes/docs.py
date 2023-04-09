from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.security import  OAuth2PasswordRequestForm
from fastapi import  Depends, HTTPException, status, Security,Request
from modules.auth import UserAuth,get_current_active_user,ACCESS_TOKEN_EXPIRE_MINUTES
from modules.documentation import app , route_doc
from models.db import UserDB,RoleDB,UploadDB, get_db
from models.validation import EmailBase, UserBase,User,UserUpdate,UserRead,UserCreate,Role,Token,Login,Response,PasswordResetRequestCreate
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

ua=UserAuth()

router = APIRouter(
    prefix="",
    tags=["Documentation"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title,
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        
    )
@router.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)

async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@router.get("/redoc", include_in_schema=False)
async def redoc_html():

    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title,
        redoc_js_url="/static/custom-redoc.standalone.js",
    )