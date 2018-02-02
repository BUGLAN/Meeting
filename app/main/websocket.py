from ext import socketio
from flask_socketio import emit, send, join_room, leave_room
from datetime import datetime
from flask import g

"""
this is websocket for chat and barrage
# auth required ???
"""

"""
使用装饰器装饰聊天函数
使其在start_time 和 end_time 里面才能进行
"""

"""
多个聊天室即是房间
使用flask-socketio 的join_room leave_room
多人聊天使用广播 同一命名空间都能接收到

如何验证身份
1. header里面加token 获取user 对象
2. 前端发送会议名称 获取Meet 对象
3. 两个人或者多个人一起聊天就讲其加入到共同的room里面
4. 验证user 和 Meet 对象 (Meet.start_time 和 Meet.end_time)
5. 传输到浏览器上
"""


def time_limited(func, meet):
    def decorator(*args, **kwargs):
        time = datetime.now().strftime('%Y-%m-%d %H:%M')
        start_time = datetime.strptime(meet.start_time, '%Y-%m-%d %H:%M')
        end_time = datetime.strptime(meet.end_time, '%Y-%m-%d %H:%M')
        if start_time < time < end_time:
            return func(*args, **kwargs)

    return decorator


# ----聊天室----
@socketio.on('connect', namespace='/ChatRoom')
def on_connect():
    # emit("response", {"msg": "link ChatRoom", "code": "200"})
    pass


@socketio.on('join', namespace='/ChatRoom')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit("response", {"msg": username + " join the " + room, "code": "200"})


@socketio.on('Chat', namespace='/ChatRoom')
def handle_chat_event(data):
    room = data['room']
    emit("response", {"msg": "chat", "code": "200"}, room=room)


@socketio.on('leave', namespace='/ChatRoom')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit("response", {"msg": username + " leave the " + room, "code": "200"}, room=room)
# ----聊天室----


# ----弹幕----
@socketio.on('connect', namespace='/barrage')
def barrage_on_connect():
    # emit("response", {"msg": "link ChatRoom", "code": "200"})
    pass


@socketio.on('join', namespace='/barrage')
def barrage_on_join(data):
    # username = data['username']
    room = data['room']
    join_room(room)
    # emit('response', {"msg": username + " join the " + room, "code": "200"})


@socketio.on('barrage', namespace='/barrage')
def handle_barrage_event(data):
    room = data['room']
    emit("response", {"msg": "barrage success", "code": "200"}, room=room)


@socketio.on('leave', namespace='/barrage')
def barrage_on_leave(data):
    # username = data['username']
    room = data['room']
    leave_room(room)
    # emit("response", {"msg": username + " leave the " + room, "code": "200"}, room=room)
# ----弹幕----
