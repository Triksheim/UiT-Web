from CMSDB import MyDb
from werkzeug.security import generate_password_hash, check_password_hash

class User():
    def __init__(self, username, email, password_hash, firstname, lastname, user_uuid, activated):
        self.username = username
        self.email = email
        self.password_hash = password_hash.replace("\"", "")
        self.firstname = firstname
        self.lastname = lastname
        self.uuid = user_uuid
        self.activated = activated
        
        self.is_active= True
        self.is_authenticated = True

    def login(username, password):
        with MyDb as db:
            user = db.get_user(username)
            if user:
                user = User(*user)
                user_pw = user.password_hash.replace("\"", "")
                if check_password_hash (user_pw, password):
                    return True
            return False

    def get_id(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)