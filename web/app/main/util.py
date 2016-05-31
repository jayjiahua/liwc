# -*- encoding: utf-8 -*-
#
# comment
#
# 2016/4/27 0027 Jay : Init

import json
import pika
import os
import csv
import StringIO
from tasks import text_analyse, matrix_analyse
# def nlpir_analyse(loc_userdict, loc_worddict, loc_classdict, file_path, keyword):
#
#     import utils.test1 as T
#     import utils.nlpir as N
#     import utils
#     reload(utils)
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
#     splitwcDict = dict()
#     splitwcDict_empty = dict()
#     mflag, msg=T.txtAnalyze(splitwcDict,dict(),splitwcDict_empty,singleWordCount,m_wordCountDict,worddict,classdict,dict_classname,word_pr_dict,file_path, keyword, ['*'] * 8, keyword)
#
#     return msg

def push_text_task(loc_userdict, loc_worddict, loc_classdict, file_path, keyword, task_id, col_text, filename):
    message = dict(loc_userdict=loc_userdict,
                   loc_worddict=loc_worddict,
                   loc_classdict=loc_classdict,
                   file_path=file_path,
                   keyword=keyword,
                   task_id=task_id,
                   col_text=col_text,
                   filename=filename)
    text_analyse.delay(message)


def push_matrix_task(filename, col_id, col_text, task_id):
    message = dict(list_filename=[filename],
                   col_id=col_id,
                   col_text=col_text,
                   task_id=task_id)
    matrix_analyse.delay(message)


def merge_rows(file_path_list):
    str_buffer = StringIO.StringIO()

    fwriter = csv.writer(str_buffer, dialect='excel')

    for file_path, filename in file_path_list:
        if os.path.isfile(file_path):
            freader = csv.reader(open(file_path, 'rb'), dialect='excel')
            for e, row in enumerate(freader):
                if e == 0:
                    row = [u"文件名".encode("gbk")] + row
                else:
                    row = [filename.encode("gbk")] + row
                fwriter.writerow(row)
        fwriter.writerow([])
    # return str_buffer
    return str_buffer.getvalue().replace("\r", "")

def merge_columns(file_path_list):
    sum_wordCount = {}
    word_set = set()
    for file_path, filename in file_path_list:
        if os.path.isfile(file_path):
            freader = csv.reader(open(file_path, 'rb'), dialect='excel')

            current_filename = ''

            for e, row in enumerate(freader):
                if e == 0 and len(row) > 1:
                    current_filename = row[1]
                    sum_wordCount[current_filename] = {}
                if e > 0 and row != [] and len(row) > 1:
                    count = 0
                    if row[1].isdigit():
                        count = int(row[1])
                    sum_wordCount[current_filename][row[0]] = count
                    word_set.add(row[0])

    filename_list = sum_wordCount.keys()
    header = [u"词".encode("gbk")] + filename_list + [u"总计".encode("gbk")]

    str_buffer = StringIO.StringIO()

    fwriter = csv.writer(str_buffer, dialect='excel')
    fwriter.writerow(header)

    for word in word_set:
        to_write_list = [word]
        total = 0
        for filename in filename_list:
            count = sum_wordCount[filename][word] if sum_wordCount[filename].get(word) else 0
            total += count
            to_write_list.append(count)
        to_write_list.append(total)
        fwriter.writerow(to_write_list)
    # return str_buffer
    return str_buffer.getvalue().replace("\r", "")