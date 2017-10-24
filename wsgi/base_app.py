import os
from os import environ
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore

app = Flask(__name__)
app.config['DEBUG'] = True

APP_ROOT = os.path.dirname(__file__)+'/'

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), "../../data/")

app.config['SECRET_KEY'] = '6435386457452384526165659634377965438689'

app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = 'fhasddihwhtl2y8f'

app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'manga_main.html'
app.config['SECURITY_LOGIN_USER_TEMPLATE'] = 'manga_main.html'

#sql_host = 'localhost'

if 'OPENSHIFT_MYSQL_DB_HOST' in os.environ.keys():
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://%s:%s@%s:3306/web"%(
        os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],
        os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'],
        os.environ['OPENSHIFT_MYSQL_DB_HOST']
    )
else:    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////web_app.db'


db = SQLAlchemy(app)

from models import User, Ruoli

user_datastore = SQLAlchemyUserDatastore(db, User, Ruoli)

security = Security(app, user_datastore)