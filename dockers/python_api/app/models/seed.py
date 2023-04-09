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
            }
           
      ],
      'wallets':[
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":35
      },
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":34
      },
      {
      "name":'XP',
      "available":0,
      "used":0,
      "user_id":36
      },
      {
      "name":'XP',
      "available":4800000,
      "used":0,
      "user_id":33
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
            }

      ],
      'uploads': [
    
            {
                "id":1,
                "name":"default",
                "path":"default",
                "ext":"jpg"
            }

      ]



    }






# This method receives a table, a connection and inserts data to that table.
def initialize_table(target, connection, **kw):
    
    tablename = str(target)
    print("SEEDING",tablename)
    if tablename in INITIAL_DATA and len(INITIAL_DATA[tablename]) > 0:
        connection.execute(target.insert(), INITIAL_DATA[tablename])