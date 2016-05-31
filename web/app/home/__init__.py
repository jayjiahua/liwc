# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/5/16 0016 Jay : Init

from flask import Blueprint

home = Blueprint('home', __name__)

from . import views