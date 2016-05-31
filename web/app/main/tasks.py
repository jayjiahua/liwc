# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/5/27 0027 Jay : Init

import datetime
import traceback
import sys
import os

nlpir_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "nlpir")
sys.path.append(nlpir_dir)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# print os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app")

import nlpir as N
import test1 as T


from app import db
from app import app as flask_app
from app.models import TextTask, TaskStatus, MatrixTask

from celery import Celery

BROKER_URL = 'amqp://guest:guest@localhost:5672//'

app = Celery('tasks', broker=BROKER_URL)

loc_wordCount = os.path.join(nlpir_dir, "Export/wordCount.csv")
loc_splitwordCount = os.path.join(nlpir_dir, "Export/splitwordCount.csv")

def nlpir_analyse(loc_userdict, loc_worddict, loc_classdict, file_path, keyword, col_text, filename):

    singleWordCount={} #记录字频
    wordCountDict={}  #记录词频
    worddict={}
    classdict={}
    word_pr_dict={} #精确的词典
    dict_classname={}

    if loc_userdict:
        N.mImportUserDict(loc_userdict)

    T.init_dict(loc_worddict,loc_classdict,worddict,classdict,dict_classname,word_pr_dict,wordCountDict,singleWordCount)
    T.init_output()

    fcDict = dict()
    fcDict['countfiles'] = 0
    m_wordCountDict = dict(wordCountDict)
    splitwcDict = dict(singleWordCount)
    splitwcDict_empty = dict()
    mflag, msg=T.txtAnalyze(splitwcDict,fcDict,splitwcDict_empty,singleWordCount,m_wordCountDict,worddict,classdict,dict_classname,word_pr_dict,file_path, keyword, ['*'] * 8, keyword, col_text)

    if mflag:

        header = ["词".encode('gbk'),"{0} | {1}".format(filename,datetime.datetime.now()).encode("gbk"),"总计".encode('gbk')]
        T.saveWordCount(m_wordCountDict,dict(),loc_wordCount, header, filename)
        T.saveWordCount(splitwcDict,splitwcDict_empty,loc_splitwordCount, header, filename)

        wordCountPath = file_path[:file_path.find(".csv")] + "(wordCount).csv"
        singleCountPath = file_path[:file_path.find(".csv")] + "(singleCount).csv"

        T.saveWordCount(m_wordCountDict,dict(),wordCountPath, header, filename)
        T.saveWordCount(splitwcDict,splitwcDict_empty,singleCountPath, header, filename)

    return msg


@app.task
def text_analyse(message):
    task_id = message.get("task_id")

    del message["task_id"]

    with flask_app.app_context():
        is_running = False
        task = TextTask.query.get(task_id)
        if task and task.status == TaskStatus.WAITING:
            is_running = True
            task.begin_time = datetime.datetime.now()
            task.status = TaskStatus.RUNNING
            db.session.add(task)
            db.session.commit()
    if is_running:
        task_status = TaskStatus.FAIL
        try:
            result_filename = nlpir_analyse(**message)
            print result_filename
            task_status = TaskStatus.SUCCESS
        except:
            exstr = traceback.format_exc()
            print exstr
            task_status = TaskStatus.FAIL
        finally:
            with flask_app.app_context():
                task = TextTask.query.get(task_id)
                task.status = task_status
                task.end_time = datetime.datetime.now()
                db.session.add(task)
                db.session.commit()

@app.task
def matrix_analyse(message):
    task_id = message.get("task_id")

    del message["task_id"]
    with flask_app.app_context():
        task = MatrixTask.query.get(task_id)
        is_running = False
        if task and task.status == TaskStatus.WAITING:
            is_running = True
            task.begin_time = datetime.datetime.now()
            task.status = TaskStatus.RUNNING
            db.session.add(task)
            db.session.commit()
    if is_running:
        task_status = TaskStatus.FAIL
        try:
            file_path = T.createMap(**message)
            T.listToMatrix([file_path])
            task_status = TaskStatus.SUCCESS
        except:
            task_status = TaskStatus.FAIL
        finally:
            with flask_app.app_context():
                task = MatrixTask.query.get(task_id)
                task.status = task_status
                task.end_time = datetime.datetime.now()
                db.session.add(task)
                db.session.commit()