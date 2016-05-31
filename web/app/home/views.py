# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/5/16 0016 Jay : Init

from . import home

from flask import render_template

@home.route('/', methods=['GET'])
@home.route('/home', methods=['GET'])
def home():
    return render_template("home.html")
