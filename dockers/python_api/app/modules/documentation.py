from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from modules.auth import set_scopes

doc_scopes=set_scopes()
doc_routes_info={
    "/users/{user_id}/":"Update users"
}
class FastDocs:
    def __init__(self):  
        self.tags_metadata = [
             {
                "name": "Wallet Management",
                "description": "Operations to view and share points used for booking screen time slots",
            },
            {
                "name": "User Authentication",
                "description": "Operations with users. The **login** logic is also here.",
            },
            {
                "name": "User Profile Management",
                "description": "Manage items. So _fancy_ they have their own docs.",
                "externalDocs": {
                    "description": "Items external docs",
                    "url": "https://google.com",
                },
            },
        ]
        self.title="Screentime XP Maximus"
        self.description="""
        Here you can earn screentime XP, transfer screentime XP and book your screentime slot 🚀
            """
        self.version="0.0.1"
        self.terms_of_service="/docs/terms/"
        self.contact={
        "name": "A Torque Digital Initiative",
        "url": "http://www.torquedigital.co.za",
        "email": "developer@torquedigital.co.za",
        }
        self.license_info={
        "name": "GNU General Public License",
        "url": "https://www.gnu.org/licenses/gpl-3.0.en.html",
        }



def route_doc(route_name):
    route_doc={}
    route_doc[route_name]={}

    if route_name not in doc_scopes.keys():
        route_doc[route_name]['permissions']="User/Role Access: Public[ALL]"
    else:
        route_doc[route_name]['permissions']=doc_scopes[route_name]
    
    if route_name not in doc_routes_info.keys():
        route_doc[route_name]['text']=""
    else:
        route_doc[route_name]['text']=doc_routes_info[route_name]+"\n\n"
    
    return route_doc[route_name]['text']+route_doc[route_name]['permissions']

fd=FastDocs()
    
app = FastAPI( title=fd.title,description=fd.description,version=fd.version,terms_of_service=fd.terms_of_service,contact=fd.contact,license_info=fd.license_info,openapi_tags=fd.tags_metadata, docs_url=None, redoc_url=None)


app.mount("/static", StaticFiles(directory="static"), name="static")