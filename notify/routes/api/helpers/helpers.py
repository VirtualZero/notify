from functools import wraps
from flask import request, abort, copy_current_request_context
from notify import app, db, mail, twilio_client
import requests
import jwt, random, string, datetime, re
from os import environ
from notify.models.verified_app import VerifiedApp
from flask_mail import Message
from threading import Thread


def validate_user_token():
    if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

            if not token:
                abort(
                    401,
                    'Error: User API key is required.'
                )

    else:
        abort(
            401,
            'Error: User API key is required.'
        )

    payload = requests.get(
        f'{environ["USER_API_URL"]}/{token}').json()

    if payload['status'] == 'failure':
        abort(
            401,
            'Invalid API Key'
        )

    return payload


def commit_new_app(verified_app):
    db.session.add(verified_app)
    db.session.commit()
    db.session.flush()

    return verified_app


def make_api_keys(vzid, app_name, appid):
    api_key = jwt.encode(
        {
            'vzid': vzid,
            'app_name': app_name,
            'appid': appid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365)
        },
        environ['JWT_SECRET_KEY']
    ).decode(
        'utf-8'
    )

    refresh_api_key = jwt.encode(
        {
            'vzid': vzid,
            'app_name': app_name,
            'appid': appid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1500)
        },
        environ['JWT_REFRESH_SECRET_KEY']
    ).decode(
        'utf-8'
    )

    return {
        'api_key': api_key,
        'refresh_api_key': refresh_api_key
    }


def add_app():
    payload = validate_user_token()
    app_name = request.get_json()['app_name']

    if VerifiedApp.query.filter_by(
        app_name=app_name
    ).first():
        abort(
            400,
            'Error: App name already exists in database.'
        )

    unique = False
    appid = ""

    while unique == False:
        for i in range(8):
            appid = f"{appid}{random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)}"

        if not VerifiedApp.query.filter_by(
            appid=appid
        ).first():
            unique = True      

    api_keys = make_api_keys(payload['vzid'], app_name, appid)      

    verified_app = VerifiedApp(
        payload['vzid'],
        appid,
        app_name,
        api_keys['api_key'],
        api_keys['refresh_api_key']
    )

    commit_new_app(verified_app)
    
    return {
        'status': 'success',
        'appid': appid,
        'api_key': api_keys['api_key'],
        'refresh_api_key': api_keys['refresh_api_key']
    }


def decode_api_key():
    if not request.headers.get('X-API-KEY'):
        abort(
            401,
            'Must include the API key.'
        )

    try:
        api_key = jwt.decode(
            request.headers['X-API-KEY'],
            environ['JWT_SECRET_KEY']
        )

    except jwt.exceptions.DecodeError:
        abort(
            401,
            'Error: Invalid API key.'
        )

    except jwt.exceptions.ExpiredSignatureError:
        abort(
            401,
            'Error: API key is expired, use your app\'s refresh API key to get a new API Key.'
        )

    except:
        abort(
            500,
            'Something went wrong.'
        )

    return api_key


def delete_app():
    api_key = decode_api_key()

    app_to_delete = VerifiedApp.query.filter_by(
        appid=api_key['appid']
    ).first()

    if not app_to_delete:
        abort(
            400,
            'App does not exist in database.'
        )

    if app_to_delete.app_name != api_key['app_name'] or \
        app_to_delete.vzid != api_key['vzid'] or \
        app_to_delete.api_key != request.headers['X-API-KEY']:
        
        abort(
            401,
            'Invalid API key.'
        )

    db.session.delete(app_to_delete)
    db.session.commit()
    
    return {
        'status': 'success',
        'message': f'{api_key["app_name"]} ({api_key["appid"]}) deleted.'
    }


def valid_email_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        email_list = request.get_json()['recipients']

        for i in email_list:
            if not re.search(
                '.+@.+\..+',
                i
            ):
                abort(
                    400,
                    'Error: At least one (1) invalid email address.'
                )
            
        return f(*args, **kwargs)

    return decorated


def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        decoded_api_key = decode_api_key()

        app_ = VerifiedApp.query.filter_by(
            appid=decoded_api_key['appid']
        ).first()

        if not app_:
            abort(
                400,
                'Error: App not in database.'
            )

        return f(*args, **kwargs)

    return decorated


def send_mail():
    data = request.get_json()

    @copy_current_request_context
    def send_message(new_message):
        mail.send(new_message)

    new_message = Message(
        data["subject"],
        sender=(
            'VirtualZero',
            'no-reply@virtualzero.tech'
        ),
        recipients=data["recipients"]
    )

    new_message.body = data["message"]
    
    sender = Thread(
        name='new_mail_sender',
        target=send_message,
        args=(new_message,)
    )

    sender.start()

    return {
        'status': 'success'
    }, 200


def send_sms():
    recipient = request.get_json()['recipient']
    sms = request.get_json()['message']

    if not re.search('^\+\d{11}$', recipient):
        abort(
            400,
            'Not a valid, US phone number. ie +18144482479'
        )

    if not recipient:
        abort(
            400,
            'Must include a recipient.'
        )

    if not sms:
        abort(
            400,
            'Must include a message to send.'
        )

    try:
        twilio_client.messages.create(
            to=recipient,
            from_=environ['TWILIO_SEND_FROM'],
            body=sms
        )

    except:
        abort(
            500,
            'Something went wrong.'
        )

    return {
        'status': 'success'
    }