# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    DEBUG = True

    # sqlalchemy
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class ProductConfig(Config):
    DB_USERNAME = 'root'   # 数据库用户名
    DB_PASSWORD = ''       # 数据库密码
    DB_PORT = 3306         # 数据库端口
    DB_NAME = 'bdc'         # 数据库名称
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@localhost:%d/%s?charset=utf8&use_unicode=0' % (DB_USERNAME, DB_PASSWORD, DB_PORT, DB_NAME)


config = {
    'product': ProductConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
