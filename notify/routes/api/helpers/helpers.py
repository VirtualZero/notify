from functools import wraps
from flask import request, abort
from notify import app, db
import requests
import jwt, random, string, datetime
from os import environ
from notify.models.verified_app import VerifiedApp


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
