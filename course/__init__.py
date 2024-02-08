from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///courses.db'
# Flask uses this secret key to sign the session cookie
app.config['SECRET_KEY'] = '9b02d00476969f0e04ca626be846d4'
db = SQLAlchemy(app)
# passing app object in Bcrypt for initializing hasing
bcrypt = Bcrypt(app)
# this object will handle all the login authentication and login sessions after user logs in
# it needs our flask app object as a parameter. because it needs to know which flask app it will manage login for
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from course import route