from ext import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


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
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    password_hash = db.Column(db.String(225))
    phone = db.Column(db.String(15), unique=True)
    company = db.Column(db.String(50))

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

    def __str__(self):
        return "<User: {} id: {}>".format(self.username, self.id)

    def __repr__(self):
        return "<User {} id: {}>".format(self.username, self.id)


class Meet(db.Model):
    __tablename__ = 'meet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(225))
    password = db.Column(db.String(20))
    create_time = db.Column(db.DateTime())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, **kwargs):
        super(Meet, self).__init__(**kwargs)
        self.create_time = datetime.now()

    def __str__(self):
        return "<Meet {}> created in {}".format(self.name, self.create_time)

    def __repr__(self):
        return "<Meet {}> created in {}".format(self.name, self.create_time)