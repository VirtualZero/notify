from functools import wraps
from flask import request, abort
from notify import app, db
import requests
import jwt, random, string
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

    verified_app = VerifiedApp(
        payload['vzid'],
        appid,
        app_name
    )

    commit_new_app(verified_app)
    
    return {
        'status': 'success',
        'appid': appid
    }
