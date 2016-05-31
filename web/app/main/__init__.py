# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/3/29 0029 Jay : Init

from flask import Blueprint
from ..models import Permission, TaskStatus
main = Blueprint('main', __name__)

from . import views

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission,
                TaskStatus=TaskStatus)
