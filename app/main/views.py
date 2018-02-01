from . import main_blueprint
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from ext import db
from flask import jsonify, request, make_response, g, send_from_directory, abort
from .models import User, Meet, ChatMessage
from datetime import datetime
from flask_httpauth import HTTPBasicAuth
import os
from config import BaseConfig

main_api = Api(main_blueprint)
auth = HTTPBasicAuth()

"""
认证 Basic Auth
两种方式
1. username:password
2. token:unused 
# unused 占位符
"""


@auth.verify_password
def verify_password(username_or_token, password):
    user = User.verify_auth_token(username_or_token)
    if not user:
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@auth.error_handler
def unauthorized():
    return make_response(jsonify({"error": "Unauthorized"}), 403)


"""
res.headers['Access-Control-Allow-Origin'] = '*'
res.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS'
res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
"""


# class AjaxTest(Resource):
#     """
#     ajax test for font people
#     """
#
#     def post(self):
#         if request.json:
#             message = {"message": "success", "status_code": 200}
#             response = make_response(jsonify(message))
#             return response
#         else:
#             message = {"message": "fail", "status_code": 200}
#             response = make_response(jsonify(message))
#             return response


# class AxiosTest(Resource):
#     """
#     axios test for font people
#     """
#
#     def post(self):
#         if request.json:
#             message = {"message": "success", "status": 200}
#             response = make_response(jsonify(message), 200)
#             return response
#         else:
#             message = {"message": "fail", "status_code": 200}
#             response = make_response(jsonify(message))
#             return response
#
#     def get(self):
#         message = {"message": "success", "status": 200}
#         response = make_response(jsonify(message), 200)
#         return response


class MeetAdmin(Resource):
    """
    # user -> meet
    # OneToMany
    # login_require
    {
        "data" :{
            "name": "meeting name ",
            "start_time": "meeting start time",
            "end_time": "meeting end time",
            "allow_people": "any" or "just somebody",
            "number": "max allow people"
        }
        "operation" : "new" or "delete" or "change" ---- Note' if change all people can get message'
    }
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('data', type=dict, help="dict must be dict type", required=True)
        self.parser.add_argument('operation', type=str, help="operation must be str type", required=True)
        self.data_parser = reqparse.RequestParser()
        self.data_parser.add_argument('name', type=str, help="name must be str type", location='data', required=True)
        self.data_parser.add_argument('start_time', type=str, help="create_time must be str", location='data')
        self.data_parser.add_argument('end_time', type=str, location='data', required=True)
        self.data_parser.add_argument('allow_people', type=str, help="allow_people must be str type", location='data'
                                      , required=True)
        self.data_parser.add_argument('number', type=int, help="number must be int type", location='data'
                                      , required=True)
        super(MeetAdmin, self).__init__()

    decorators = [auth.login_required]

    def post(self):
        args = self.parser.parse_args()
        data_args = self.data_parser.parse_args(req=args)
        if args['operation'] == 'new':
            meet = Meet(
                name=data_args['name'],
                password='123456'
            )
            db.session.add(meet)
            db.session.commit()
            return jsonify({"id": meet.id, "name": meet.name, "username": g.user.username,
                            'start_time': meet.create_time.strftime('%Y-%m-%d %H:%M')})
        elif args['operation'] == 'delete':
            return "delete Meeting"
        elif args['operation'] == 'change':
            return "change Meeting"
        else:
            return make_response(jsonify({"error": "格式错误"}), 400)


class ChatApi(Resource):
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

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('user', type=dict, help="user must be dict type")
        self.parser.add_argument('message', type=str, help="message must be str type")
        self.parser.add_argument('allow_people', type=str, help="allow_people must be str type")
        self.parser.add_argument('meet_name', type=str, help="allow_people must be str type")
        self.user_parser = reqparse.RequestParser()
        self.user_parser.add_argument('username', type=str, help="username must be str type", location='user')
        self.user_parser.add_argument('send_time', type=str, help="send_time must be str type", location='user')
        super(ChatApi, self).__init__()

    decorators = [auth.login_required]

    def post(self):
        args = self.parser.parse_args()
        user_args = self.user_parser.parse_args(req=args)
        user = User.query.filter(User.username == user_args['username']).first()
        if user:
            # 将 message 存入到 ChatMessage 表中
            try:
                chat_msg = ChatMessage(
                    message=args['message'],
                    user_id=user.id,
                    meet_id=Meet.query.filter_by(name=args['meet_name']).first().id
                )
                db.session.add(chat_msg)
                db.session.commit()
            except KeyError:
                return {"message": "no this meeting_room"}
            response = {
                "user": {
                    "username": user.username,
                },
                "message": request.json['message'],
            }
            user_args['send_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({"error": "用户名错误"}), 400)
            #  聊天和会议的api 由这个提供


meet_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'meet_portrait': fields.String,
}


class Meets(Resource):
    """
    会议搜索查询
    模糊搜索
    {
        meet_name:
    }
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('meet_name', type=str, help="meet_name must be str type", required=True)
        super(Meets, self).__init__()

    @marshal_with(meet_fields)
    def post(self):
        args = self.parser.parse_args()
        meets = Meet.query.filter(Meet.name.like('%{}%'.format(args['meet_name']))).all()
        return meets


user_fields = {
    'id': fields.Integer,
    'head_portrait': fields.String,
    'username': fields.String,
    'phone': fields.String,
    'company': fields.String
}


class Users(Resource):
    """
    用户搜索查询
    模糊搜索
    need fields
    {
        username:
    }
    """

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, help="username must be str type", required=True)
        super(Users, self).__init__()

    @marshal_with(user_fields)
    def post(self):
        args = self.parser.parse_args()
        users = User.query.filter(User.username.like('%{}%'.format(args['username']))).all()
        return users


from werkzeug.datastructures import FileStorage


class FileStorageArgument(reqparse.Argument):
    """
    此类用于接受处理 flask-restful 收到的所有上传文件
    """

    def convert(self, value, op, *args, **kwargs):
        if self.type is FileStorage:
            # 如果 Argument 类型为文件，那么返回的 value 则为文件对象
            # 然后在 put 或 post 方法里用这个对象读取文件就好了。
            return value
        super(FileStorageArgument, self).convert(*args, **kwargs)


class HeadPortrait(Resource):
    """
    picture save path
    """
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser(argument_class=FileStorageArgument)
        self.parser.add_argument('file', required=True, type=FileStorage, location='files')
        super(HeadPortrait, self).__init__()

    def post(self):
        args = self.parser.parse_args()
        file = args['file']
        path = os.path.join(BaseConfig.UPLOAD_FOLDER, g.user.username)
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            file.save(os.path.join(path, file.filename))
            user = g.user
            user.head_portrait = str('file' + '/' + g.user.username + '/' + file.filename)
            db.session.add(user)
            db.session.commit()
            return {"message": "上传成功"}
        except:
            response = make_response(jsonify({"message": "上传失败"}), 400)
            return response


class MeetUploadFile(Resource):
    """
    上传会议附件
    目前仅能上传一个服务间
    """
    decorators = [auth.login_required]

    def __init__(self):
        self.parser = reqparse.RequestParser(argument_class=FileStorageArgument)
        self.parser.add_argument('file', required=True, type=FileStorage, location='files')
        super(MeetUploadFile, self).__init__()

    def post(self, MeetName):
        args = self.parser.parse_args()
        file = args['file']
        meet = Meet.query.filter_by(name=MeetName).first_or_404()  # 没有相关会议名返回404
        path = os.path.join(BaseConfig.UPLOAD_FOLDER, g.user.username, meet.name)
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            file.save(os.path.join(path, file.filename))
            meet.attachment = str('file' + '/' + meet.name + '/' + file.filename)
            return {"message": "上传成功"}
        except:
            response = make_response(jsonify({"message": "上传失败"}), 400)
            return response


class MeetDownLoadFile(Resource):
    """
    Meet download file api
    """
    decorators = [auth.login_required]

    def get(self, MeetName):
        meet = Meet.query.filter_by(name=MeetName).first_or_404()
        if meet and meet.attachment:
            try:
                filename = os.path.basename(meet.attachment)
                directory = os.path.join(BaseConfig.UPLOAD_FOLDER, meet.name)
                full_path = os.path.join(directory, filename)
                if os.path.exists(full_path):
                    response = make_response(send_from_directory(directory, filename, as_attachment=True), 200)
                    response.headers["Content-Disposition"] = "attachment; filename={}".format(
                        filename.encode().decode('latin-1'))
                    return response
                else:
                    return {"message": "文件不存在"}, 400
            except:
                return {"message": "下载失败"}, 400
        else:
            abort(404)


# main_api.add_resource(AjaxTest, '/AjaxTest')
# main_api.add_resource(AxiosTest, '/AxiosTest')
main_api.add_resource(MeetAdmin, '/MeetAdmin')
main_api.add_resource(ChatApi, '/ChatApi')
main_api.add_resource(Meets, '/meets')
main_api.add_resource(Users, '/users')
main_api.add_resource(HeadPortrait, '/upload_portrait')
main_api.add_resource(MeetUploadFile, '/meet_upload_file/<string:MeetName>')
main_api.add_resource(MeetDownLoadFile, '/meet_download_file/<string:MeetName>')


