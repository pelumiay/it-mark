from enum import unique
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__) #creates a flask app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db' #configure myshop database


#app = Flask(__name__)
app.config['SECRET_KEY'] = '6bdbe190331388b4adf0d2a2'

#ENV = 'prod'


#if ENV == 'dev':
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'

#else:
   # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fekjtgfydxieoe:b388d656a0f5214a3dbff4cacc5083d437c8047320c535f72a4d9eac7adc62ca@ec2-52-6-77-239.compute-1.amazonaws.com:5432/d1kkbe89td43jm'
    
    
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

def getApp():
    return app
from market import routes