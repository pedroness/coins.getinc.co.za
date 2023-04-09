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
        self.title="FastAPI Boiler Auth App"
        self.description="""
        Launch Pad for awesome Projects 🚀
            """
        self.version="0.0.1"
        self.terms_of_service="/docs/terms/"
        self.contact={
        "name": "Torque Digital PTY(Ltd)",
        "url": "http://torquedigital.co.za",
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

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title=fd.title,
#         version=fd.version,
#         description=fd.description,
#         routes=app.routes,
        
#     )
    
#     openapi_schema["info"]["x-logo"] = {
#         "url": "/static/logo.png"
#     }
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi


app.mount("/static", StaticFiles(directory="static"), name="static")