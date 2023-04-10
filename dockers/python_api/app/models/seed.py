from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Database initial data
INITIAL_DATA = {
      'roles': [
            {
                  'id': 1,
                  "name": 'Administrator', 
                  "permissions":{"routes": ["/users/me/", "/users/role/", "/qr/print/", "/users/{user_id}/"]}
            },
            {
                  'id': 2,
                  "name": 'Project Manager', 
                  "permissions":{"routes": ["/users/me/", "/users/role/", "/qr/print/"]}
            },
            {
                  'id': 3,
                  "name": 'User', 
                  "permissions":{"routes": ["/users/me/"]}
            },
            {
                  'id': 4,
                  "name": 'Parent', 
                  "permissions":{"routes": ["/users/me/", "/wallets/me/"]}
            },
            {
                  'id': 5,
                  "name": 'Kid', 
                  "permissions":{"routes": ["/users/me/", "/wallets/me/"]}
            }
           
      ],
      'uploads': [
    
            {
                "id":1,
                "name":"default",
                "path":"default",
                "ext":"jpg"
            }

      ],
      'users': [
    
            {
                "first_name":"Admin",
                "last_name":"Root",
                "email":"admin@beagenius.co.za",
                "profile_upload_id":1,
                "username":"administrator",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 1
            },            {
                "first_name":"Project",
                "last_name":"Manager",
                "email":"projectmanager@beagenius.co.za",
                "profile_upload_id":1,
                "username":"projectmanager",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 2
            },            {
                "first_name":"User",
                "last_name":"Bob",
                "email":"user@beagenius.co.za",
                "profile_upload_id":1,
                "username":"user",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 3
            },
            {
                "first_name":"Parent",
                "last_name":"Bob",
                "email":"parent@beagenius.co.za",
                "profile_upload_id":1,
                "username":"parent",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 4
            },
            {
                "first_name":"Kid1",
                "last_name":"1",
                "email":"kid1@beagenius.co.za",
                "profile_upload_id":1,
                "username":"kid1",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 5
            },
            {
                "first_name":"Kid2",
                "last_name":"2",
                "email":"kid2@beagenius.co.za",
                "profile_upload_id":1,
                "username":"kid2",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 5
            },
            {
                "first_name":"Kid3",
                "last_name":"3",
                "email":"kid3@beagenius.co.za",
                "profile_upload_id":1,
                "username":"kid3",
                "disabled":False,
                "hashed_password": pwd_context.hash("password"),
                "role_id": 5
            }

      ],
      'wallets':[
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":7
      },
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":6
      },
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":5
      },
      {
      "name":'XP',
      "available":4800000,
      "used":0,
      "user_id":4
      }
      ]
      



    }






# This method receives a table, a connection and inserts data to that table.
def initialize_table(target, connection, **kw):
    
    tablename = str(target)
    print("SEEDING",tablename)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])