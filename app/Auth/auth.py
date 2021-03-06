from . import auth_blueprint
from flask_restful import Resource, Api, reqparse
from ..main.models import User
from ext import db
from flask import make_response, jsonify

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
parser.add_argument('check_password', type=str)
parser.add_argument('phone', type=str, help="username must be str")
parser.add_argument('company', type=str, help="username must be str")
parser.add_argument('email', type=str)


class Login(Resource):
    """
    username password
    email password
    login
    """

    def post(self):
        args = parser.parse_args()
        user = User.query.filter_by(username=args['username']).first()
        email = User.query.filter_by(email=args['email']).first()
        phone = User.query.filter_by(phone=args['phone']).first()
        if user or email or phone and user.verify_password(args['password']):
            response = make_response(jsonify({"token": user.generate_auth_token().decode('ascii')}), 200)
            response.set_cookie(key='token', value=user.generate_auth_token().decode('ascii'), secure=False)
            return response
        if user and not user.verify_password(args['password']):
            return {"message": "密码错误"}, 409
        else:
            return {"message": "请先注册"}, 200


def check_register(args):
    if len(args['username']) >= 6:
        if args['password'] == args['check_password']:
            if '@' in args['email']:
                return True
    return False


class Register(Resource):
    """
    后端验证表单数据
    check_register()
    password == check_password
    username >= 6
    email format check
    1831353087@qq.com
    """

    def post(self):
        args = parser.parse_args()
        if check_register(args):
            try:
                user = User(
                    head_portrait=args['head_portrait'],
                    username=args['username'],
                    password=args['password'],
                    email=args['email'],
                    phone=args['phone'],
                    company=args['company'])
                db.session.add(user)
                db.session.commit()
            except:
                return {"message": "用户名或电话或已被使用"}, 409

        return {"message": "注册成功"}, 200


class Logout(Resource):
    def post(self):
        response = make_response(jsonify({"message": "logout success"}), 200)
        # response.set_cookie('token', '', expires=0)
        response.delete_cookie('token')
        return response


auth_api.add_resource(Login, '/login')
auth_api.add_resource(Register, '/register')
auth_api.add_resource(Logout, '/logout')
