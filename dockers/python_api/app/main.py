from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from modules.documentation import app 
from routes import auth,users,docs,wallets
templates = Jinja2Templates(directory="templates")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(docs.router)
app.include_router(wallets.router)
app.include_router(auth.router)
app.include_router(users.router)







        

    
          
