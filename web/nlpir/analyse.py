# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/4/27 0029 Jay : Init

#!/usr/bin/env python

import test1 as T
import nlpir as N
import pika
import json
import os, sys
import datetime
import traceback

from pika.exceptions import ConnectionClosed

# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "web"))
# print os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))), "web")
# sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "web"))
# from app import db, app
# from app.models import TextTask, TaskStatus, MatrixTask
#
# loc_wordCount = os.path.abspath(os.path.dirname(__file__)) + "/Export/wordCount.csv"
# loc_splitwordCount = os.path.abspath(os.path.dirname(__file__)) + "/Export/splitwordCount.csv"
#
# def nlpir_analyse(loc_userdict, loc_worddict, loc_classdict, file_path, keyword, col_text, filename):
#
#     singleWordCount={} #记录字频
#     wordCountDict={}  #记录词频
#     worddict={}
#     classdict={}
#     word_pr_dict={} #精确的词典
#     dict_classname={}
#
#     if loc_userdict:
#         N.mImportUserDict(loc_userdict)
#
#     T.init_dict(loc_worddict,loc_classdict,worddict,classdict,dict_classname,word_pr_dict,wordCountDict,singleWordCount)
#     T.init_output()
#
#     fcDict = dict()
#     fcDict['countfiles'] = 0
#     m_wordCountDict = dict(wordCountDict)
#     splitwcDict = dict(singleWordCount)
#     splitwcDict_empty = dict()
#     mflag, msg=T.txtAnalyze(splitwcDict,fcDict,splitwcDict_empty,singleWordCount,m_wordCountDict,worddict,classdict,dict_classname,word_pr_dict,file_path, keyword, ['*'] * 8, keyword, col_text)
#
#     if mflag:
#         T.saveWordCount(m_wordCountDict,dict(),loc_wordCount,["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')], filename)
#         T.saveWordCount(splitwcDict,splitwcDict_empty,loc_splitwordCount,["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')], filename)
#
#         wordCountPath = file_path[:file_path.find(".csv")] + "(wordCount).csv"
#         singleCountPath = file_path[:file_path.find(".csv")] + "(singleCount).csv"
#
#         T.saveWordCount(m_wordCountDict,dict(),wordCountPath,["词".encode('gbk'),"{0} | {1}".format(filename,datetime.datetime.now()),"总计".encode('gbk')], filename)
#         T.saveWordCount(splitwcDict,splitwcDict_empty,singleCountPath,["词".encode('gbk'),"{0} | {1}".format(filename,datetime.datetime.now()),"总计".encode('gbk')], filename)
#
#     return msg
#
# if __name__ == '__main__':
#
#
#     def callback(ch, method, properties, body):
#         print " [x] Received %r" % (body,)
#         message = json.loads(body)
#         task_type = message.get("task_type")
#         task_id = message.get("task_id")
#
#         del message["task_type"]
#         del message["task_id"]
#
#         if task_type == "text":
#             with app.app_context():
#                 is_running = False
#                 task = TextTask.query.get(task_id)
#                 if task and task.status == TaskStatus.WAITING:
#                     is_running = True
#                     task.begin_time = datetime.datetime.now()
#                     task.status = TaskStatus.RUNNING
#                     db.session.add(task)
#                     db.session.commit()
#             if is_running:
#                 task_status = TaskStatus.FAIL
#                 try:
#                     result_filename = nlpir_analyse(**message)
#                     print result_filename
#                     task_status = TaskStatus.SUCCESS
#                 except:
#                     exstr = traceback.format_exc()
#                     print exstr
#                     task_status = TaskStatus.FAIL
#                 finally:
#                     with app.app_context():
#                         task = TextTask.query.get(task_id)
#                         task.status = task_status
#                         task.end_time = datetime.datetime.now()
#                         db.session.add(task)
#                         db.session.commit()
#         elif task_type == "matrix":
#             with app.app_context():
#                 task = MatrixTask.query.get(task_id)
#                 is_running = False
#                 if task and task.status == TaskStatus.WAITING:
#                     is_running = True
#                     task.begin_time = datetime.datetime.now()
#                     task.status = TaskStatus.RUNNING
#                     db.session.add(task)
#                     db.session.commit()
#             if is_running:
#                 task_status = TaskStatus.FAIL
#                 try:
#                     file_path = T.createMap(**message)
#                     T.listToMatrix([file_path])
#                     task_status = TaskStatus.SUCCESS
#                 except:
#                     task_status = TaskStatus.FAIL
#                 finally:
#                     with app.app_context():
#                         task = MatrixTask.query.get(task_id)
#                         task.status = task_status
#                         task.end_time = datetime.datetime.now()
#                         db.session.add(task)
#                         db.session.commit()
#         print " [x] Done -> %r" % task_id
#
#         ch.basic_ack(delivery_tag = method.delivery_tag)
#
#     def main():
#         connection = pika.BlockingConnection(pika.ConnectionParameters(
#                 host='localhost'))
#         channel = connection.channel()
#
#         channel.queue_declare(queue='new_task_queue', durable=True)
#         print ' [*] Waiting for messages. To exit press CTRL+C'
#
#         channel.basic_qos(prefetch_count=1)
#         channel.basic_consume(callback,
#                               queue='task_queue')
#
#         try:
#             channel.start_consuming()
#         except ConnectionClosed:
#             main()
#
#     main()

if __name__ == '__main__':

    from tasks import text_analyse, matrix_analyse
    def callback(ch, method, properties, body):
        print " [x] Received %r" % (body,)
        message = json.loads(body)
        task_type = message.get("task_type")
        del message["task_type"]
        if task_type == "text":
            text_analyse.delay(message)
        elif task_type == "matrix":
            matrix_analyse.delay(message)
        print " [x] Done -> %r" % (body,)

        ch.basic_ack(delivery_tag = method.delivery_tag)

    def main():
        connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)
        print ' [*] Waiting for messages. To exit press CTRL+C'

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback,
                              queue='task_queue')

        try:
            channel.start_consuming()
        except ConnectionClosed:
            main()

    main()