from ext import socketio
from flask_socketio import emit, send

"""
this is websocket for chat and barrage
# auth required ???
"""


@socketio.on('my event', namespace='/test')
def handle_my_custom_event(json):
    print("received json: " + str(json))
    emit('response', {'code': '200', "msg": "socket ok"})


@socketio.on('message')
def handle_message(msg):
    print('received message: ' + msg)
    send('no useful')
