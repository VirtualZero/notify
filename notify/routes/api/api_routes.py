from flask import request, abort, Blueprint
from notify import app, db
from flask_restplus import Api, Resource, fields
import requests
from notify.routes.api.helpers.helpers import add_app, delete_app

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
    def post(self):
        return add_app()


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
        return delete_app()