from . import main_blueprint
from flask_restful import Resource, Api
from .models import Meet
from ext import db
from flask import jsonify, request, make_response

main_api = Api(main_blueprint)


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
            return make_response(jsonify({"message": "格式错误"}), 400)
        if 'name' and 'allow_people' and 'number' not in request.json['data']:
            return make_response(jsonify({"message": "data 格式错误"}), 400)
        if request.json['operation'] not in ['new', 'delete', 'change']:
            return make_response(jsonify({"message": "operation 格式错误"}), 400)
        if request.json['operation'] == 'new':
            meet = Meet(name=request.json['data']['name'], password='123456')
            db.session.add(meet)
            db.session.commit()
            return jsonify({"id": meet.id, "name": meet.name, "password": meet.password,
                            'create_time': meet.create_time})
        if request.json['operation'] == 'delete':
            return "delete Meeting"
        if request.json['operation'] == 'change':
            return "change Meeting"
        else:
            return "big error"


class Chat(Resource):
    """
    {
        "user" : {
            name: "user.name",
            "send_time": "datetime.datetime.now()"
        }
        "message": "send message"
        "allow_people": "all", "just one", "part of people"
        "meeting_room": "meet's name"
    }
    """
    def post(self):
        pass


main_api.add_resource(MeetAdmin, '/MeetAdmin')