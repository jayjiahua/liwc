# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

from inspect import isfunction, getmembers
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from config import config
from . import jinja2_filters

import os

app = Flask(__name__)

bootstrap = Bootstrap()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'

def create_app(config_name):
    # app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)

    custom_filters = {
        name: function for name, function in getmembers(jinja2_filters) if isfunction(function)
    }
    app.jinja_env.filters.update(custom_filters)

    from .home import home as home_blueprint
    app.register_blueprint(home_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix="/main")

    from .chart import chart as chart_blueprint
    app.register_blueprint(chart_blueprint, url_prefix="/chart")

    # 附加路由和自定义的错误页面
    return app


app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
