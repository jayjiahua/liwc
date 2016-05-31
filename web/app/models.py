# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/4/24 0024 Jay : Init

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask.ext.login import UserMixin, AnonymousUserMixin
from flask import current_app
from . import login_manager

import datetime

class Permission:
    NORMAL = 0x01
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_default_roles():
        roles = {
            u'管理员': {
                'permissions': (0xff),
                'description': 'administrator'
            },
            u'普通用户': {
                'permissions': Permission.NORMAL,
                'description': 'user'
            }
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r]['permissions']
            role.description = roles[r]['description']
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    fullname = db.Column(db.String(64), default="")
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    expire_at = db.Column(db.Date, nullable=True)

    dict = db.relationship('Dict', backref='user')
    libraries = db.relationship('Library', backref="user")
    text_tasks = db.relationship('TextTask', backref='user', lazy="dynamic")
    matrix_tasks = db.relationship('MatrixTask', backref='user', lazy="dynamic")


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def is_expired(self):
        if self.expire_at == None:
            return False
        elif self.expire_at >= datetime.date.today():
            return False
        else:
            return True

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role.permissions & permissions == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def gravatar(self, size=100, default='identicon', rating='g'):
        return ''

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    def __repr__(self):
        return '<User %r>' % self.username

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])


    @staticmethod
    def insert_admin():
        users = {
            'admin': {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'role': u'管理员',
                'fullname': u'超级管理员'
            },
        }
        for u, v in users.items():
            user = User.query.filter_by(username=u).first()
            if user is None:
                user = User(username=u, email=v['email'], confirmed=True, fullname=v['fullname'])
                user.password = v['password']
                user.role = Role.query.filter_by(name=v['role']).first()
            db.session.add(user)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    # user_id is a unicode string, needed to be converted it to int
    user = User.query.get(int(user_id))
    if user and user.is_expired():
        return None
    return user

class Dict(db.Model):
    __tablename__ = 'dicts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)
    filename = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

class Library(db.Model):
    __tablename__ = 'libraries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.datetime.now)

    word_dict = db.Column(db.String(128), nullable=False)
    class_dict = db.Column(db.String(128), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

class TaskStatus:
    WAITING = 1
    RUNNING = 2
    SUCCESS = 3
    FAIL = 4

class TextTask(db.Model):
    __tablename__ = 'text_tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    keyword = db.Column(db.Text)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    begin_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=TaskStatus.WAITING)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    library_name = db.Column(db.String(64), nullable=False)
    user_dict_name = db.Column(db.String(64))


    def get_status(self):
        dic = {
            TaskStatus.WAITING: u"等待分析",
            TaskStatus.RUNNING: u"正在分析",
            TaskStatus.FAIL:    u"分析失败",
            TaskStatus.SUCCESS: u"分析成功"
        }
        return dic[self.status]

class MatrixTask(db.Model):
    __tablename__ = 'matrix_tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    begin_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=TaskStatus.WAITING)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)


    def get_status(self):
        dic = {
            TaskStatus.WAITING: u"等待分析",
            TaskStatus.RUNNING: u"正在分析",
            TaskStatus.FAIL:    u"分析失败",
            TaskStatus.SUCCESS: u"分析成功"
        }
        return dic[self.status]
