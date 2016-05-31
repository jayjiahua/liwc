# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/5/16 0016 Jay : Init

from . import chart

from flask import render_template

@chart.route('/words', methods=['GET'])
def words():
    return render_template("words_map.html")

@chart.route('/cities', methods=['GET'])
def cities():
    return render_template("cities_net.html")



