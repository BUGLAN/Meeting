from . import main_blueprint
from flask_restful import Resource, Api
from .models import Meet
from ext import db
from flask import jsonify, request, make_response
from .models import User
from flask_cors import CORS

main_api = Api(main_blueprint)
CORS(main_blueprint, resources=r'/*')


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
            "username": "user.username",
            "send_time": "datetime.datetime.now()"
        }
        "message": "send message"
        "allow_people": "all", "just one", "part of people" (可选)
        "meeting_room": "meet's name"
    }
    """
    def post(self):
        if 'user' and 'message' and 'meeting_room' not in request.json:
            return make_response(jsonify({"error": "格式错误"}), 400)
        # user = request.json['user']['name']
        if request.json['user']['username'] and request.json['user']['send_time'] is None:
            return make_response(jsonify({"error": "格式错误"}), 400)
        user = User.query.filter(User.username == request.json['user']['username']).first()
        if user:
            return make_response(jsonify(
                {
                    "user": {
                        "username": user.username,
                        "send_time": request.json['user']['send_time']
                    },
                    "message": request.json['message'],
                    "status": 200
                }), 200)
        else:
            return make_response(jsonify({"error": "用户名错误"}), 400)


class AjaxTest(Resource):
    """
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    """
    def post(self):
        if request.json:
            message = {"message": "success", "status_code": 200}
            response = make_response(jsonify(message))
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
            response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
            return response
        else:
            message = {"message": "success", "status_code": 200}
            res = make_response(jsonify(message))
            return res


# need more knowledge abort flask-restful
main_api.add_resource(MeetAdmin, '/MeetAdmin')
main_api.add_resource(Chat, '/ChatApi')
main_api.add_resource(AjaxTest, '/AjaxTest')