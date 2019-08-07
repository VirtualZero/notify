from flask import request, abort, Blueprint
from notify import app
from flask_restplus import Api, Resource, fields
from notify.routes.api.helpers.helpers import (
    add_app, delete_app,
    valid_email_required,
    api_key_required,
    send_mail,
    send_sms
)


# Blueprint

blueprint = Blueprint(
    'api',
    __name__,
    url_prefix='/api/v1'
)

authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(
    blueprint,
    authorizations=authorizations,
    title='VIRTUALZERO NOTIFICATION API',
    version='1.1',
    description='coming soon',
    validate=True
)

app.register_blueprint(blueprint)


# Namespaces

ns_mail = api.namespace(
    'mail',
    description='coming soon'
)

ns_sms = api.namespace(
    'sms',
    description='coming soon'
)

ns_app = api.namespace(
    'app',
    description='coming soon'
)


# Models

new_app = api.model(
    'New App',
    {
        'app_name': fields.String('app_name', required=True)
    }
)

api_mail = ns_mail.model(
    'Mail',
    {
        'recipients': fields.List(fields.String, required=True),
        'subject': fields.String('subject', required=True),
        'message': fields.String('message', required=True)
    }
)

api_sms = ns_sms.model(
    'SMS',
    {   
        'recipient': fields.String('recipient', required=True),
        'message': fields.String('message', required=True)
    }
)


# Routes

@ns_app.route('/new-app')
class NewApp(Resource):
    @ns_app.expect(new_app)
    @ns_app.header(
        'X-API-KEY',
        'Must include the user API key in header.'
    )
    @ns_app.doc(
        description='coming soon',
        security='apikey',
        responses={
            200: 'Success',
            400: 'Bad Request',
            401: 'Not Authorized',
            500: 'Something went wrong.'
        }
    )
    def put(self):
        return add_app(), 200


@ns_app.route('/delete-app')
class DeleteApp(Resource):
    @ns_app.header(
        'X-API-KEY',
        'Must include the app API key in header.'
    )
    @ns_app.doc(
        description='coming soon',
        security='apikey',
        responses={
            200: 'Success',
            400: 'Bad Request',
            401: 'Not Authorized',
            500: 'Something went wrong.'
        }
    )
    def delete(self):
        return delete_app(), 200


@ns_mail.route('/send-mail')
class SendMail(Resource):
    @ns_mail.expect(api_mail)
    @ns_mail.header(
        'X-API-KEY',
        'Must include the app API key in the header.'
    )
    @ns_mail.doc(
        description='coming soon',
        security='apikey',
        responses={
            200: 'Success',
            400: 'Bad Request',
            401: 'Not Authorized',
            500: 'Something went wrong.'
        }
    )
    @api_key_required
    @valid_email_required
    def post(self):
        return send_mail(), 200


@ns_sms.route('/send-sms')
class SendSMS(Resource):
    @ns_sms.expect(api_sms)
    @ns_sms.header(
        'X-API-KEY',
        'Must include the app API key in the header.'
    )
    @ns_sms.doc(
        description='coming soon',
        security='apikey',
        responses={
            200: 'Success',
            400: 'Bad Request',
            401: 'Not Authorized',
            500: 'Something went wrong.'
        }
    )
    @api_key_required
    def post(self):
        return send_sms(), 200
