# from flask import request, jsonify, make_response
from . import auth_blueprint
from flask_restful import Resource, Api, reqparse
from ..main.models import User
from ext import db

auth_api = Api(auth_blueprint)

"""
register format
{
	
	"username": "",
	"password": "",
    "phone": "",
    "company": ""
}
"""

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, help="username must be str")
parser.add_argument('password', type=str, help="password must be str")
parser.add_argument('phone', type=str, help="username must be str")
parser.add_argument('company', type=str, help="username must be str")


class Login(Resource):
    def post(self):
        args = parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        if user and user.verify_password(args['password']):
            return {"token": user.generate_auth_token().decode('ascii')}, 200
        if user and not user.verify_password(args['password']):
            return {"message": "密码错误"}, 409
        else:
            return {"message": "请先注册"}, 200


class Register(Resource):
    def post(self):
        args = parser.parse_args()
        try:
            user = User(
                username=args['username'],
                password=args['password'],
                phone=args['phone'],
                company=args['company'])
            db.session.add(user)
            db.session.commit()
        except:
            return {"message": "用户名或电话已被使用"}, 409

        return {"message": "注册成功"}, 200


class Logout(Resource):
    def post(self):
        pass


auth_api.add_resource(Login, '/login')
auth_api.add_resource(Register, '/register')
auth_api.add_resource(Logout, '/logout')
