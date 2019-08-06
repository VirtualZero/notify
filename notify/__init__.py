from flask import Flask
from os import environ
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from twilio.rest import Client

app = Flask(__name__)

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQL_DATABASE_URI']
app.config['SQLALCHEMY_ECHO'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Flask_Mail
app.config.update(dict(
    DEBUG=False,
    MAIL_SERVER=environ['MAIL_SERVER'],
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME=environ['MAIL_USERNAME'],
    MAIL_PASSWORD=environ['MAIL_PASSWORD'],
    MAIL_DEFAULT_SENDER=environ['MAIL_DEFAULT_SENDER'])
)

mail = Mail(app)


# Twilio
account_sid = environ['TWILIO_ACCOUNT_SID']
auth_token = environ['TWILIO_AUTH_TOKEN']

twilio_client = Client(
    account_sid,
    auth_token
)


# Models
from notify.models.verified_app import VerifiedApp

# Routes
from notify.routes.api import api_routes
