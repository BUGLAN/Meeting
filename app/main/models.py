from ext import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from config import BaseConfig


class User(db.Model):
    """
    会议的用户表和管理员表
    id : 编号
    username : 用户名
    password : 密码
    password_hash : 储存password的hash码
    phone : 电话号码
    company : 人员所属公司
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    head_portrait = db.Column(db.String(128))
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    password_hash = db.Column(db.String(225))
    phone = db.Column(db.String(15), unique=True)
    company = db.Column(db.String(50))
    meets = db.relationship('Meet', backref='users')
    create_time = db.Column(db.DateTime())

    # ---password hash
    @property
    def password(self):
        raise AttributeError('password is not a readable attributes')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---password hash

    def generate_auth_token(self, expiration=60000):
        s = Serializer(BaseConfig.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(BaseConfig.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.query.get(data['id'])
        return user

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.create_time = datetime.now()

    def __str__(self):
        return "<User: {} id: {}>".format(self.username, self.id)

    def __repr__(self):
        return "<User {} id: {}>".format(self.username, self.id)


class Meet(db.Model):
    """
    会议室的信息
    """
    __tablename__ = 'meet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225))
    password = db.Column(db.String(20))
    password_hash = db.Column(db.String(225))
    meet_portrait = db.Column(db.String(128))
    create_time = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # ---password hash
    @property
    def password(self):
        raise AttributeError('password is not a readable attributes')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---password hash

    def __init__(self, **kwargs):
        super(Meet, self).__init__(**kwargs)
        self.create_time = datetime.now()

    def __str__(self):
        return "<Meet {}> created in {}".format(self.name, self.create_time)

    def __repr__(self):
        return "<Meet {}> created in {}".format(self.name, self.create_time)


class ChatMessage(db.Model):
    """
    记录聊天的message
    """
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meet_id = db.Column(db.Integer, db.ForeignKey('meet.id'))
    create_time = db.Column(db.DateTime())

    def __init__(self, **kwargs):
        super(ChatMessage, self).__init__(**kwargs)
        self.create_time = datetime.now()

    def __str__(self):
        return "<ChatRoom {}>".format(Meet.query.get(self.meet_id).name)

    def __repr__(self):
        return "<ChatRoom {}>".format(Meet.query.get(self.meet_id).name)
