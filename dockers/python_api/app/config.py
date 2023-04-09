import os

environ_instance_vars = ["PY_API_HOST", "PY_WEB_HOST"]
# os.environ['PY_API_HOST']='http://localhost:8000'
# os.environ['PY_WEB_HOST']='http://localhost:3000'


environ_email_vars = [
    "PY_EMAIL_FROM",
    "PY_EMAIL_USER",
    "PY_EMAIL_PASSWORD",
    "PY_EMAIL_HOST",
    "PY_EMAIL_PORT",
]

# os.environ['PY_EMAIL_FROM']='bullet@bulletqr.co.za'
# os.environ['PY_EMAIL_USER']='bullet@bulletqr.co.za'
# os.environ['PY_EMAIL_PASSWORD']="B00let@@@@@"
# os.environ['PY_EMAIL_HOST']='mail.bulletqr.co.za'
# os.environ['PY_EMAIL_PORT']='465'


environ_db_vars = [
    "PY_DB_USER",
    "PY_DB_PASSWORD",
    "PY_DB_HOST",
    "PY_DB_PORT",
    "PY_DB_DATABASE",
]

# os.environ['PY_DB_USER']='odoo'
# os.environ['PY_DB_PASSWORD']="123"
# os.environ['PY_DB_HOST']='0.0.0.0'
# os.environ['PY_DB_PORT']='5432'
# os.environ['PY_DB_DATABASE']='bullet_qr'


env_vars = environ_email_vars + environ_instance_vars + environ_db_vars

env_not_found = []


class env:
    def __init__(self):
        self.env = {}
        for env_var in env_vars:
            try:
                self.env[env_var] = os.environ[env_var]
            except (KeyError) as error:
                env_not_found.append(env_var)

        if len(env_not_found) > 0:
            raise Exception(
                "These required Enviroment Variables were not found:", env_not_found
            )
