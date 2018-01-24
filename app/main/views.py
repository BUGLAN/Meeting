from . import main_blueprint
from flask_restful import Resource, Api, reqparse, fields
from .models import Meet
from ext import db
from flask import jsonify, request, make_response
from .models import User
from flask_cors import CORS
from datetime import datetime

main_api = Api(main_blueprint)
CORS(main_blueprint, resources=r'/*')
"""
res.headers['Access-Control-Allow-Origin'] = '*'
res.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS'
res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
"""


class AjaxTest(Resource):
    """
    ajax test for font people
    """

    def post(self):
        if request.json:
            message = {"message": "success", "status_code": 200}
            response = make_response(jsonify(message))
            return response
        else:
            message = {"message": "fail", "status_code": 200}
            response = make_response(jsonify(message))
            return response


class AxiosTest(Resource):
    """
    axios test for font people
    """

    def post(self):
        if request.json:
            message = {"message": "success", "status": 200}
            response = make_response(jsonify(message), 200)
            return response
        else:
            message = {"message": "fail", "status_code": 200}
            response = make_response(jsonify(message))
            return response

    def get(self):
        message = {"message": "success", "status": 200}
        response = make_response(jsonify(message), 200)
        return response


class MeetAdmin(Resource):
    """
    # user -> meet
    # OneToMany
    # login_require
    # post a
    {
        "data" :{
            "name": "meeting name",
            "create_time": "meeting start time",
            "end_time": "meeting end time",
            "allow_people": "any" or "just somebody",
            "number": "max allow people"
        }
        "operation" : "new" or "delete" or "change" ---- Note' if change all people can get message'
    }
    """

    def post(self):
        if 'data' and 'operation' not in request.json:
            return make_response(jsonify({"error": "格式错误"}), 400)
        elif 'name' and 'allow_people' and 'number' not in request.json['data']:
            return make_response(jsonify({"error": "data 格式错误"}), 400)
        elif request.json['operation'] not in ['new', 'delete', 'change']:
            return make_response(jsonify({"error": "operation 格式错误"}), 400)
        elif request.json['operation'] == 'new':
            meet = Meet(name=request.json['data']['name'], password='123456')
            db.session.add(meet)
            db.session.commit()
            return jsonify({"id": meet.id, "name": meet.name, "password": meet.password,
                            'create_time': meet.create_time})
        elif request.json['operation'] == 'delete':
            return "delete Meeting"
        elif request.json['operation'] == 'change':
            return "change Meeting"
        else:
            return make_response(jsonify({"error": "格式错误"}), 400)


class Chat(Resource):
    """
    {
        "user" : {
            "username": "user.username", # 前端发送
            "send_time": "datetime.now()" #  由后端发送
        }
        "message": "send message" # 前端发送
        "allow_people": "all", "just one", "part of people" (可选) # 前端发送 默认为['all']
        "meeting_room": "meet's name" # 前端发送
    }
    """

    def post(self):
        if 'user' and 'message' and 'meeting_room' not in request.json:
            return make_response(jsonify({"error": "格式错误"}), 400)
        # user = request.json['user']['name']
        if request.json['user']['username'] is None:
            return make_response(jsonify({"error": "格式错误"}), 400)
        user = User.query.filter(User.username == request.json['user']['username']).first()
        if user:
            response = {
                "user": {
                    "username": user.username,
                },
                "message": request.json['message'],
            }
            response['user']['send_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({"error": "用户名错误"}), 400)
            #  聊天和会议的api 由这个提供


# class UserRegister(Resource):
#     """
#     user register api
#     format : {
#         "username": "",
#         "password": "",
#         "phone"; "",
#         "company": ""
#     }
#     # create_time 无需定义实例化的时候会有__init__()自动转换
#     """
#
#     def post(self):
#         args = register_parser.parse_args()
#         user = User(
#             username=args['username'],
#             password=args['password'],
#             phone=args['phone'],
#             company=args['phone']
#         )
#         db.session.add(user)
#         db.session.commit()
#         return "用户注册成功"
#
#
# class UserLogin(Resource):
#     """
#     user login api
#     format: {
#         "username"; "",
#         "password": ""
#     }
#     """
#
#     def post(self):
#         pass


main_api.add_resource(MeetAdmin, '/MeetAdmin')
main_api.add_resource(Chat, '/ChatApi')
main_api.add_resource(AjaxTest, '/AjaxTest')
main_api.add_resource(AxiosTest, '/AxiosTest')
# main_api.add_resource(UserRegister, '/register')
