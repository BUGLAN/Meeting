from ext import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from config import BaseConfig


class Permission:
    """
    权限表
    ADMINISTRATOR 超级管理人员 工作人员访问
    MEETER 创建会议的用户
    USER 普通用户
    """
    __tablename__ = 'permission'
    USER = 0x01
    MEETER = 0x02
    ADMINISTRATOR = 0xff


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.USER, True),
            'Admin': (Permission.MEETER | Permission.USER, False),
            'ADMINISTRATOR': (Permission.ADMINISTRATOR, False)
        }
        """
        | 按位或运算符：只要对应的二个二进位有一个为1时，结果位就为1。
        & 按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0
        """
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __str__(self):
        return "<Role {}>".format(self.name)

    def __repr__(self):
        return "<Role {}>".format(self.name)


class User(db.Model):
    """
    会议的用户表和管理员表
    id  编号
    username  用户名
    password  密码(不可见)
    password_hash 储存password的hash码
    email 仅一个
    phone  电话号码 仅一个
    company  人员所属公司
    meets 关联的会议信息表
    create_time 用户创建时间
    msgs 关联 聊天记录
    verify_password 验证密码
    generate_auth_token 生成token
    verify_auth_token 验证token
    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    head_portrait = db.Column(db.String(128), default='file/head_portrait.jpg.')
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    password_hash = db.Column(db.String(225))
    email = db.Column(db.String(30), unique=True)
    phone = db.Column(db.String(15), unique=True)
    company = db.Column(db.String(50))
    meets = db.relationship('Meet', backref='users')
    create_time = db.Column(db.DateTime())
    msgs = db.relationship('ChatMessage', backref='users')
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

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

    def generate_auth_token(self, expiration=6000):
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

    def can(self, permission):
        return self.role is not None and (self.role.permissions & permission) == permission

    def is_meeter(self):
        """
        判断是否为会议的创建者 permissions == 3
        """
        return self.can(Permission.USER | Permission.MEETER)

    def is_admin(self):
        """
        判断是否系统管理员 permissions == 255
        """
        return self.can(Permission.ADMINISTRATOR)

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
    start_time = db.Column(db.DateTime())
    attachment = db.Column(db.String(225))
    end_time = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    msgs = db.relationship('ChatMessage', backref='meets')

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
