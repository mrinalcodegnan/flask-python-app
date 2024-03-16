from flask_restful import Resource, reqparse
from flask import jsonify, make_response
from werkzeug.security import check_password_hash

class Login(Resource):
    def __init__(self, collection):
        self.collection = collection

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()

        email = args['email']
        password = args['password']

        user = self.collection.find_one({'email': email})

        if user:
            stored_password = user.get('password')
            if check_password_hash(stored_password, password):
                return make_response(jsonify({'message': 'Login successful'}), 200)
            else:
                return make_response(jsonify({'message': 'Invalid password'}), 401)
        else:
            return make_response(jsonify({'message': 'User not found'}), 404)