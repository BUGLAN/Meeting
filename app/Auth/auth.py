from flask import request, jsonify, make_response
from . import auth_blueprint
from flask_restful import Resource, Api
from ..main.models import User
from ext import db

auth_api = Api(auth_blueprint)


"""
{
	"data": {
		"username": "123456",
		"password": "123456"
	}
}
"""


def check_data_format(json):
    """
    format is right return data
    format is error return a message: "格式不正确"
    """
    pass


class Login(Resource):
    def post(self):
        if not 'data' in request.json and not request.json['data']['username'] and not request.json['username']:
            return make_response(jsonify({"message": "格式错误"}), 400)

        else:
            check_data_format(request.json['data'])
            # check_data_format()
            # user = User(username=request.json['data']['username'],
            #            password=request.json['data']['password'],)
            # 此处存储格式正确和不为空的

            # login user
            return make_response(jsonify({"message": "注册成功"}), 200)


class Register(Resource):
    def post(self):
        if 'data' not in request.json or not request.json['data']['username'] or not request.json['data']['password']:
            return make_response(jsonify({"message": "格式错误"}), 400)

        else:
            check_data_format(request.json['data'])
            if User.query.filter_by(username=request.json['data']['username']).first():
                return make_response(jsonify({"message": "该用户名已存在, 请修改您的用户名"}), 409)

            if request.json['data']['phone'] and User.query.filter_by(phone=request.json['data']['phone']).first():
                return make_response(jsonify({"message": "该号码已存在,请更换号码"}), 409)

            user = User(username=request.json['data']['username'],
                        password=request.json['data']['password'],
                        phone=request.json['data']['phone'],
                        company=request.json['data']['company'],)
            db.session.add(user)
            db.session.commit()
            return make_response(jsonify({"message": "注册成功"}), 200)


auth_api.add_resource(Login, '/login')
auth_api.add_resource(Register, '/register')
