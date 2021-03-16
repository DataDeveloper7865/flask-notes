from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy 

db = SQLAlchemy()

bcrypt = Bcrypt()

class User(db.Model):

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)


    @classmethod
    def register(cls, username, password, email, first_name, last_name):

        hashed_password = bcrypt.generate_password_hash(password).decode('utf8')

        return cls(username=username, 
            password=hashed_password, 
            email=email, 
            first_name=first_name, 
            last_name=last_name)

    @classmethod
    def authenticate(cls, username, password):

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False



def connect_db(app):
    db.app = app
    db.init_app(app)
