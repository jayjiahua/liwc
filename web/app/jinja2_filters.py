# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/4/28 0028 Jay : Init

def timedelta_format(value):
    # arbitrary number of seconds
    s = value.total_seconds()
    # hours
    hours = s // 3600
    # remaining seconds
    s = s - (hours * 3600)
    # minutes
    minutes = s // 60
    # remaining seconds
    seconds = s - (minutes * 60)
    # total time
    return '%d:%02d:%02d' % (hours, minutes, seconds)

def datetime_format(value):
    return value.strftime('%Y/%m/%d %H:%M:%S')