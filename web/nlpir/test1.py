#! /usr/bin/env python
#coding=utf-8
#luokailun5
import csv
import repr
import re
import nlpir as N
import os
import chardet
import sys
import datetime
import syscontent
reload(sys)
sys.setdefaultencoding( "utf-8" )

loc_wordfilter = os.path.abspath(os.path.dirname(__file__)) + "/Import/wordFilter.txt"
loc_singleword = os.path.abspath(os.path.dirname(__file__)) + "/Import/singleword.csv"
loc_outputfile = os.path.abspath(os.path.dirname(__file__)) + "/Import/outputFilesSelection.csv"

maxInt = sys.maxint
decrement = True

while decrement:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

def delnull(x):
    return x!='' and x.strip()!=''

###########################################################################################
# @function 初始化结果文件的输出（targert(error),targert(import), targert(word),targert(total),原始的）
# @para void
# @return void
####
def init_output():
    with open(os.path.dirname(__file__) + "/Import/outputFilesSelection.csv",'rb') as ofile:
        oreader = csv.reader(ofile,dialect='excel')
        for elem in oreader:
            if elem[0] in syscontent.output_dict.keys():
                syscontent.output_dict[elem[0]] = int(elem[2])  #syscontent记录每一类的文件是否需要输出(即输出选择)

        #print syscontent.output_dict


######################################################
# @function 初始化词语词典和类词典
# @para worddict   {word: [class] }dictionary     empty
#       classdict     {class:number }dictionary  empty
#       dict_classname  {class：class explanation}dictionary empty
#       word_pr_dict    {word : true|false}dictionary   empty
#       wordCountDict   {word :  number}dictionary empty
#       singleWordCount  {singleword : number} dictionary empty
# @return void

def init_dict(loc_worddict,loc_classdict, worddict,classdict,dict_classname,word_pr_dict,wordCountDict,singleWordCount):
    single_reader = csv.reader(open(loc_singleword),dialect='excel')
    for e,elem in enumerate(single_reader):
        if e>0:
            singleWordCount[elem[0]] = 0

    with open(loc_worddict, 'rb') as wordfile:
            wordreader = csv.reader(wordfile,dialect='excel')
            classreader = csv.reader(open(loc_classdict,'rb'),dialect='excel')
            for e,w_row in enumerate(wordreader):
                if e>0 :
                    temp = w_row[0]
                    m_word,num=re.subn(r"(\*)",'.',temp)  #replace '*' in the word with '.'
                    new_w_row=filter(delnull,w_row)   #filter the list by deleteing the useless element ''
                    #new_w_row=filter(' ',new_w_row)
                    worddict[m_word]=new_w_row[1:]    #init the (word:class )dictionary
                    #print worddict
                    wordCountDict[m_word] = 0        #初始化记录词频的词典

                    word_pr_dict[m_word]=num       # judge whether is the precision word or not
                                                   # if num ==0 is precision word


                    for key in new_w_row[1:]:
                        if classdict.has_key(key) ==False:         #key.strip()!="" and
                            classdict[key]=0                     #init the (class:number )dictionary             for e,key in enumerate(worddict):

            for e,row in enumerate(classreader):
                if e>0:
                    dict_classname[row[0]] = row[1]

def init_spiltwcDict(loc_splitwordCount):
    mreader=csv.reader(open(loc_splitwordCount,'rb'),dialect='excel')
    mdict = dict()
    for row in mreader:
        mdict[row[0]]=0
    return mdict


########################################
# @function 导入词典（格式  类别(名称) ：词语集合）
# @para  loc_newDict 导入词典的文件路径
#        worddict  （词-类)词典
#        classdict  (类-数量)词典
#        dict_classname (类-解释名称)词典
#        loc_worddict    import/word.csv
#        loc_classdict   import/class.csv
# @return void
def importDict(loc_newDict,worddict,classdict,dict_classname,loc_worddict,loc_classdict):

    nd_reader = csv.reader(open(loc_newDict,'rb'),dialect='excel')
    nameTonum = dict()
    for num in dict_classname:
       nameTonum[dict_classname[num]] = num  #初始化 {classname : class} 字典

    list_class = dict_classname.values()   #list所有类的解释名称
    list_word = worddict.keys()            #list所有词的名称

    list_num = sorted(dict_classname.keys())  # 排序所有类(number),用于生成新的类(number)

    max=list_num[0]
    if list_num[len(list_num)-1]>max:
        max = list_num[len(list_num)-1]

    #改造classdict，dict_classname，worddict
    for e,row in enumerate(nd_reader):
        if e>0:
            name_class = row[0]
            #如果类名已存在，查找对应的数字编码
            if name_class in list_class :
                num_class = nameTonum[name_class]
            #否则新建类名对应的数字编码
            else:
                num_class = str(int(max)+1)
                classdict[name_class] = 0
                dict_classname[num_class] = name_class
            #对于每一个词,看看是否存在，如果存在并且（插入）类别不存在，则插入； 如何不存在，在worddict里添加新的 {word:[class]}记录
            for m_word in row[1:]:
                if m_word.strip() =="":
                    continue
                m=m_word.decode('gbk').encode('utf-8')
                if m in list_word:
                    if int(num_class) > int(max) or not num_class in worddict[m]:
                        worddict[m].append(num_class)
                    print 'yes:'+m_word
                else:
                    klist = list()
                    klist.append(num_class)
                    worddict[m] = klist
                    print 'no:'+m_word


    #重写import/word.csv 和import/class.csv
    word_writer = csv.writer(open(loc_worddict,'wb'),dialect='excel')
    class_writer = csv.writer(open(loc_classdict,'wb'),dialect='excel')
    word_writer.writerow(['词'.encode('gbk'),'类别'.encode('gbk')])
    class_writer.writerow(['类别'.encode('gbk'),'解释'.encode('gbk')])
    for row in worddict:
        m=row.decode('utf-8','ignore').encode('gbk','ignore')
        word_writer.writerow([m]+worddict[row])
    for row in dict_classname:
        class_writer.writerow([row]+[dict_classname[row]])

#############################################
#@function: 导入词典，按类别名称导入
#@para   ks 类别名称
#        dict_classname  (类-解释名称)词典
#        worddict     （词-类)词典
#        loc_file    保存文件的路径
def exportDictHandler(ks,dict_classname,worddict,loc_file):
    class_num = '-1'
    for key in dict_classname:
        print dict_classname[key]
        if dict_classname[key] == ks:
            class_num = key
            break

    if class_num =='-1':
        return False

    list_word = list()
    for mword in worddict:
        if class_num in worddict[mword]:
            list_word.append(mword)

    word_writer = csv.writer(open(loc_file+'.csv','wb'),dialect='excel')
    word_writer.writerow(['类别'.encode('gbk'),'词'.encode('gbk')])
    word_writer.writerow([ks]+list_word)
    return True

#############################################
#

def saveWordCount(wordCountDict,wordCountDict_new,loc_wordCount,header,filename):
    if os.path.isfile(loc_wordCount):
        sum_wordCount=dict()
        freader = csv.reader(open(loc_wordCount,'rb'),dialect='excel')

        header = list()
        words = wordCountDict.keys()
        for e,row in enumerate(freader):
            if e == 0:
                header = row
                header.insert(len(row)-1,"{0} | {1}".format(filename,datetime.datetime.now()).encode("gbk"))
                current_len = len(row)
            if e > 0 and row != [] and len(row) > 1:
                sum_wordCount[row[0]]=row[1:-1]
                total = 0
                try:
                    total = int(row[-1])
                except:
                    pass
                word_count = wordCountDict.get(row[0], 0)
                sum_wordCount[row[0]].append(word_count)
                sum_wordCount[row[0]].append(word_count + total)

                if row[0] in words:
                    words.remove(row[0])

        for key in words:
            sum_wordCount[key] = [0] * (current_len - 3) + [wordCountDict[key]] * 2
               #sum_wordCount[key].append(wordCountDict_new)
        fwriter = csv.writer(open(loc_wordCount,'wb'),dialect='excel')
        fwriter.writerow(header)
        for elem in sum_wordCount:
            fwriter.writerow([elem] + sum_wordCount[elem])

    else:
        fwriter = csv.writer(open(loc_wordCount,'wb'),dialect='excel')
        fwriter.writerow(header)
        for elem in wordCountDict:
            fwriter.writerow([elem,wordCountDict[elem],wordCountDict[elem]])

    #清空
    # for elem in wordCountDict:
    #     wordCountDict[elem] =0


def wrap_txtAnalyze(a):
    try:
        return txtAnalyze(*a)
    except (Exception),err:
        print "test1.py@wrap_txtAnalyze:Error when return txtAnalyze!"



#fcDict 多进程：统计有多少文件完成了
def txtAnalyze(splitwcDict,splitwcDict_empty,fcDict,singleWordCount,wcDict,worddict,classdict,dict_classname,word_pr_dict,filename,limit_word,limit_option,var_exact, col_text):
    with open(filename.encode("gbk"), 'rb') as csvfile:

        init_output() #初始化要输出的文件

        #创建局部的wordCountDict用于单词计数
        m_wordCountDict = dict.fromkeys(wcDict.keys(),0)
        list_singleword = singleWordCount.keys()

        word_list=[]     # (1)paragram (2)split_word (3)match_word
        header_class_list=[]    # header , mark the class
        num_user_list = 0
        num_err_txt =0          #the number of the error text which this program can not handle
        flag_limit_word = 1      # mark the type of limited word , 0 nothing ;1 indicate one word ;2 indicates conjunction of word; 3 disconjunction
        m_sum_classdict = dict(classdict)           #mark the sum of the number of class
        num_txt_sat = 0                     #满足限制文本数
        str_starttime=''
        str_endtime=''


        # new的 包括转发ID数，词数，句子数，四字词语数
        sum_turnId = 0
        sum_sentence = 0
        sum_word = 0
        sum_fourword = 0

        #2015.1.13 分词词频词典（局部：针对多进程来说）
        m_splitwordCount = dict(splitwcDict)
        m_splitwordCount_empty = dict()
        ####
        #filename_add="_target" ;  #文件追加部分
        ##############################################################
        # keyword limitation
        list_limitword = list()   #the list words the user type in

        if limit_word =='':
            flag_limit_word = 0
        elif re.search(r'\+',limit_word):
            list_limitword = limit_word.split('+')
            flag_limit_word = 2
        elif re.search(r'\|',limit_word):
            list_limitword = limit_word.split('|')
            flag_limit_word = 3
        else:
            list_limitword = [limit_word]

        filename_add='_'.join(list_limitword) #文件追加关键词

        m_filename=re.sub(r"(.csv)",'_',filename)
        spamreader = csv.reader((line.replace('\0','') for line in csvfile), dialect='excel')
        #######################################################
        filterreader = open(loc_wordfilter)
        dict_filter = dict()
        list_filter = list()
        for line in filterreader:
               line=line.strip()
               if line!="":
                   filterword=line
                   dict_filter[filterword] = 0
                   list_filter.append(filterword)
        ##############################################################


        dict_limitword = {}.fromkeys(list_limitword,0)        # dict , witch caculate the (limit word: number)
        ###############################################################


        #可以选择文本处理的列

        col_handle_dist=[0, col_text, 0]
        # with open(os.path.dirname(__file__) + "\\Import\\col_handle.csv",'rb') as colfile:
        #     colreader = csv.reader(colfile,dialect='excel')
        #     for col_row in colreader:
        #         col_handle_dist.append(int(col_row[1]))


        list_buffer_org = list()   #内存缓冲
        list_buffer_word = list()  #内存缓冲
        list_buffer_error = list()

        for e,row in enumerate(spamreader):
                if row ==None:
                    continue
                if e == 0:

                    #寻找处理的列
                    #for col_e,col_k in enumerate(row):
                    #    if col_k in col_handle_list:
                    #        print col_k+" 已找到, 在第".encode('gbk')+str(col_e)+"列".encode("gbk")
                    #        col_num = col_num-1
                    #        col_handle_dist[col_k] = col_e

                    #if col_num > 0:
                    #    print "error:有未找到的列！"
                    #    print col_handle_list
                    #    exit(0)

                    #计算时间限定
                    if limit_option[2] =='*' and limit_option[5] =='*':
                        flag_limit_time = False
                    else:
                        flag_limit_time = True

                        if limit_option[2] =='*':
                            str_starttime+='1000-1-1'
                        elif limit_option[3] =='*':
                            str_starttime+=limit_option[2]
                            str_starttime+='-1-1'
                        elif limit_option[4]=='*':
                            str_starttime=limit_option[2]+'-'+limit_option[3]+'-1'
                        else:
                            str_starttime=limit_option[2]+'-'+limit_option[3]+'-'+limit_option[4]

                        #print str_starttime

                        if limit_option[5] =='*':
                            str_endtime+='3000-1-1'
                        elif limit_option[6] =='*':
                            str_endtime+=limit_option[5]
                            str_endtime+='-12-31'
                        elif limit_option[7]=='*':
                            str_endtime=limit_option[5]+'-'+limit_option[6]+'-31'
                        else:
                            str_endtime=limit_option[5]+'-'+limit_option[6]+'-'+limit_option[7]

                        #print str_endtime

                        d_start = datetime.datetime.strptime(str_starttime, '%Y-%m-%d')
                        d_end = datetime.datetime.strptime(str_endtime, '%Y-%m-%d')

                    ##############################################
                    #写header
                    row.insert(2,"分词结果".encode('gbk'))
                    #print classdict.keys()

                    header_class_list = sorted(classdict.keys(),key=lambda d:int(d))  # sort the class as 1,2,3 ....(dict has no order)
                    sort_classlist = list(header_class_list)
                    header_limitword = dict_limitword.keys()
                    header_new = ['词数'.encode('gbk'),'句子数'.encode('gbk'),'每句话词数'.encode('gbk'),'转发人数'.encode('gbk'),'每个ID里平均句子数'.encode('gbk'),'每个ID里平均词数'.encode('gbk'),'每个ID里句子词数'.encode('gbk'),'4字以上词数量'.encode('gbk')]

                    for i,elem in enumerate(header_limitword):
                        header_limitword[i] = ('限定词-'+elem).encode('gbk')

                    for i,elem in enumerate(header_class_list):
                        header_class_list[i] = dict_classname[elem]
                    list_buffer_org.append(row+header_new+['用户id列表'.encode('gbk'),'用户数'.encode('gbk')]+header_limitword+header_class_list)

                else:
                    num_turnId = 0
                    num_sentence = 0
                    num_word = 0
                    num_fourword = 0
                    try:
                        text = row[col_handle_dist[1]]
                    except IndexError,err :
                        continue

                    #create_map(user,text,mapwriter)
                    user_result = re.findall(r"(//@[^@]+:|@[^@|:]+|@[^@])",text)
                    num_turnId = len(re.findall(r"(//@)",text))+1
                    #text = re.sub(r"//@[^@]+:",'。'.encode('gbk'),text)
                    newtext = re.sub(r"(//@[^@]+:|@[^@|:]+|@[^@])",'\t',text) #get the new text whose username is deleted
                    row[col_handle_dist[1]]=newtext
                    #print newtext
                    word_list=[]
                    word_list.append(newtext) #(1)paragram


                    #######################################################
                    #分词

                    flag = True
                    w_split_string ='*'     #(2)split_word
                    try:
                            #wlist= seg.cut(newtext.decode('gbk'))
                            if newtext!="" and newtext!=None:

                                #2015.1.13  把两个分词变为一个分词
                                wlist,wlist_pure,num_sentence= N.Seg_purelist(newtext.decode('gbk').encode('utf-8'))

                                for mw in wlist_pure:
                                    if len(mw) >=12:   #计算四字词语
                                        num_fourword+=1

                                    '''
                                    i=0
                                    j=i+4
                                    while j<=len(mw):
                                        singleword = mw[i:j-1].encode('gbk','ignore')
                                        print singleword
                                        if singleword in list_singleword:
                                            singleWordCount[singleword]+=1
                                        i=j
                                        j=j+4
                                    '''
                                num_word = len(wlist_pure)-num_sentence
                                w_split_string='  '.join(wlist).encode('gbk')


                    except (UnicodeEncodeError,UnicodeDecodeError) ,err:
                            #print 'can not handle this paragram!',e,err
                            #errorwriter.writerow(row)
                            if syscontent.output_dict['(error)'] == 1:
                                list_buffer_error.append(row)
                            num_err_txt+=1
                            flag=False
                    else:
                            wlist = w_split_string.split('  ')        #w_split_string是jbk编码的
                            if e% 100 == 0:
                                print e,'finished   >>  from ('+str(os.getpid())+')'
                            #print e,'finished   >>  from ('+str(os.getpid())+')'

                            ######2015.1.13 统计了分词的词频（不是指定的词频）
                            if syscontent.output_dict['Export/splitwordCount.csv'] == 1:
                                for splitword in wlist:
                                    if splitword in m_splitwordCount.keys():
                                        m_splitwordCount[splitword]+=1
                                    else:
                                        m_splitwordCount_empty[splitword]=1
                            ######

                    word_list.append(w_split_string)     #(2)split_word
                    if syscontent.output_dict['(error)']  == 1:
                          list_buffer_word.append(word_list)
                    #wordwriter.writerow(word_list)       #写一个总的分词结果
                    word_list=[]



                    #################################################################
                    #限定计算（限定关键词）

                    m_dict_limitword = {}.fromkeys(list_limitword,0)      # 记录每一条微博的限定关键词次数
                    if flag and flag_limit_word!=0:
                        if var_exact == 0:
                            for elem in list_limitword:
                                match_limitword=re.findall(elem,newtext.decode('gbk'))                    #先从未分词的文本入手
                                m_dict_limitword[elem]+=len(match_limitword)
                                #dict_limitword[elem]+=len(match_limitword )                #总的
                        else:
                            for elem in list_limitword:
                                match_limitword=wlist.count(elem.encode('gbk'))
                                m_dict_limitword[elem]+=match_limitword

                        if flag_limit_word == 1 or flag_limit_word ==2:        #合取
                            for v in m_dict_limitword.values():
                                if v == 0:
                                    flag= False
                                    break
                        elif flag_limit_word ==3:
                            flag= False
                            for v in m_dict_limitword.values():
                                if v>0:
                                    flag = True
                                    break
                    # #限定计算（限定地点）
                    # if flag and limit_option[0]!='*':
                    #     flag = False
                    #     if re.search(limit_option[0],row[col_handle_dist[2]].decode('gbk')) and (limit_option[1] =='*' or re.search(limit_option[1],row[col_handle_dist[2]].decode('gbk')) ):
                    #             flag = True
                    # #限定计算（限定时间）
                    # if flag and flag_limit_time:
                    #
                    #     str_d=row[col_handle_dist[0]].strip().strip('"')
                    #     #print str_d
                    #     d_m=datetime.datetime.strptime(str_d, '%Y-%m-%d %H:%M:%S')
                    #     #print d_start,d_end,d_m
                    #
                    #     if (d_m - d_end).days >0 or (d_m - d_start).days <0:
                    #         flag = False




                    ##############################################################
                    #过滤限定后：
                    if flag:
                        num_txt_sat+=1

                        for elem in list_limitword:
                            dict_limitword[elem]+=m_dict_limitword[elem]                #计算关键词出现的总的次数，其中m_dict_limitword为上面限定计算出现的
                                                                                        #就是说如果一个record在上面限定没有过滤掉，那么我们就计算累加它的限定词出现次数
                        for liword in list_filter:
                            dict_filter[liword]+=wlist.count(liword)

                        m_classdict = dict(classdict)                      # 记录每一条微博的类出现的次数
                        #(2014/8/7) wmatch ="match: "  #(3)match_word

                        #对于worddict里面的每一个单词，看看它是否在wlist(分词结构，gbk编码)里面出现
                        for key in worddict:

                            if key in list_filter:     #如果在词是需要过滤的词，则不计算它
                                continue

                            match_list=[]                               #记录匹配的词语，列表
                            if word_pr_dict[key] == 0:                  #当该词为精确查找时
                                num = wlist.count(key)
                                #(2014/8/7) match_list.append(key.decode('gbk'))
                            else:
                                num = 0
                                for split_word in wlist:                 #wlist是分词后的词语列表
                                    match_list=re.findall(key.decode('gbk','ignore'),split_word.decode('gbk','ignore'))
                                    num+=len(match_list)

                            if num>0:
                                for item in worddict[key]:
                                    m_classdict[item]+=num
                                    m_sum_classdict[item]+=num

                                m_wordCountDict[key]+=num     #累计词频


                        ######################################################################
                        #准备写数据文件（每一条记录）

                        result_limitword = m_dict_limitword.values()  #计算$限定词$的次数
                        '''
                        sort_dict=sorted(m_classdict.items(), key=lambda d:int(d[0])) #按顺序排列好每个$词$的出现的次数（因为字典是无序的）
                        list_result=[]
                        for k,v in sort_dict:
                            list_result.append(v)
                        '''
                        #sort_dict=sorted(m_classdict.items(), key=lambda d:int(d[0])) #按顺序排列好每个$词$的出现的次数（因为字典是无序的）
                        list_result=[]
                        for key in sort_classlist:   #sort_classlist是按顺序排好的(数字order)的类别
                            list_result.append(m_classdict[key])  #把类别的统计数量存到list_result去

                        num_user_list+=len(user_result)      #$用户数$



                        list_new=[]         #新的，包括$词数$、$句子数$等
                        list_new.append(num_word)
                        list_new.append(num_sentence)
                        sum_word+=num_word               #sum_*都是总结的，total文件里面的
                        sum_sentence+=num_sentence

                        if num_sentence!=0:
                            list_new.append(float(num_word)/float(num_sentence))
                        else:
                            list_new.append(0)
                        list_new.append(num_turnId)
                        list_new.append(float(num_sentence)/float(num_turnId))
                        list_new.append(float(num_word)/float(num_turnId))
                        sum_turnId+=num_turnId

                        if num_sentence!=0:
                            list_new.append(float(num_word)/float(num_sentence)/float(num_turnId))

                        else:
                            list_new.append(0)
                        list_new.append(num_fourword)
                        sum_fourword +=num_fourword

                        #(2014/8/7) 插入新的分词结果
                        row.insert(2,w_split_string)

                        if syscontent.output_dict['(org)'] == 1 or syscontent.output_dict['(import)'] == 1:
                            list_buffer_org.append(row+list_new+[" ".join(user_result),len(user_result)]+result_limitword+list_result)

                        #不再先写文件，而是存进了list_buffer_org里面(上一行)，效率对比??
                        #spamwriter.writerow(row+list_new+[" ".join(user_result),len(user_result)]+result_limitword+list_result)
                        #spamwriter_split.writerow(row+list_new+[" ".join(user_result),len(user_result)]+result_limitword+list_result)


        ########################################################
        #print str(os.getpid())+" : writing files......"
        #写文件
        try:
            if syscontent.output_dict['(org)'] == 1:
                spamwriter = csv.writer(open(m_filename+'target_'+filename_add+'.csv','wb'),dialect='excel')
                for elem in list_buffer_org:
                    spamwriter.writerow(elem)

            if syscontent.output_dict['(import)'] == 1:
                spamwriter_split = csv.writer(open(m_filename+'target(import)_'+filename_add+'.csv','wb'),dialect='excel')
                for elem in list_buffer_org:
                    spamwriter_split.writerow(elem)

            if syscontent.output_dict['(word)'] == 1:
                wordwriter = csv.writer(open(m_filename+'target(word).csv','wb'),dialect='excel')
                for elem in list_buffer_word:
                    wordwriter.writerow(elem)


            if syscontent.output_dict['(error)'] == 1:
                errorwriter = csv.writer(open(m_filename+'target(error).csv','wb'),dialect='excel')
                for elem in list_buffer_error:
                    errorwriter.writerow(elem)

            if os.path.exists(m_filename+'target(total).csv'):
                flag_file_exist = True
            else:
                flag_file_exist =False
            if syscontent.output_dict['(total)'] == 1:
                spamwriter_sum = csv.writer(open(m_filename+'target(total).csv','ab'),dialect='excel')

        except IOError ,error :
            return False,error



        #########################################################
        #总结部分

        #################################################################
        #并发汇总到manager.dict, 即wcDict

        for elem in m_wordCountDict:
            wcDict[elem] += m_wordCountDict[elem]
        #################################################################
        #2015.1.13 汇总统计分词词频
        for key in m_splitwordCount:
            if key in splitwcDict.keys():
                splitwcDict[key]+=m_splitwordCount[key]
            else:
                splitwcDict[key]=m_splitwordCount[key]

        for key in m_splitwordCount_empty:
            if key in splitwcDict_empty.keys():
                splitwcDict_empty[key] += m_splitwordCount_empty[key]
            else:
                splitwcDict_empty[key] = m_splitwordCount_empty[key]

        #################################################################
        sort_dict=sorted(m_sum_classdict.items(), key=lambda d:int(d[0]))
        list_result_sum=[]
        for k,v in sort_dict:
            list_result_sum.append(v)

        if syscontent.output_dict['(org)'] == 1:
            spamwriter.writerow([])
            spamwriter.writerow(['总结（共）:'.encode('gbk')])

        w_limit_time = (str_starttime+'至'+str_endtime).encode('gbk')
        w_limit_place = (limit_option[0]+' '+limit_option[1]).encode('gbk')



        list_sum_wst= list()
        list_sum_wst.append(sum_word)
        list_sum_wst.append(sum_sentence)
        if sum_sentence!= 0:
            list_sum_wst.append(float(sum_word)/float(sum_sentence))
        else:
            list_sum_wst.append(0)
        list_sum_wst.append(sum_turnId)
        list_sum_wst.append(float(sum_sentence)/float(sum_turnId))
        list_sum_wst.append(float(sum_word)/float(sum_turnId))
        if sum_sentence!= 0:
            list_sum_wst.append(float(sum_word)/float(sum_sentence)/float(sum_turnId))
        else:
             list_sum_wst.append(0)
        list_sum_wst.append(sum_fourword)

        if syscontent.output_dict['(org)'] == 1:
            spamwriter.writerow(['处理文本总数/输入文本总数'.encode('gbk'),'符合搜索要求文本数'.encode('gbk'),'ID总数'.encode('gbk'),'时间限定'.encode('gbk'),'地点限定'.encode('gbk')]+header_limitword+header_new+header_class_list)
            spamwriter.writerow([str(e-num_err_txt)+'/'+str(e),num_txt_sat,num_user_list,w_limit_time,w_limit_place ]+dict_limitword.values()+list_sum_wst+list_result_sum)
                #  +list_limitword +header_limitword



        if not flag_file_exist and syscontent.output_dict['(total)'] == 1:
            spamwriter_sum.writerow(['处理文本总数/输入文本总数'.encode('gbk'),'符合搜索要求文本数'.encode('gbk'),'ID总数'.encode('gbk'),'时间限定'.encode('gbk'),'地点限定'.encode('gbk'),'限定词'.encode('gbk'),'限定词次数'.encode('gbk')]+header_new+header_class_list)

        s_limitword =" ".join(dict_limitword.keys()).encode('gbk')
        s_num_limitword=" ".join(str(i) for i in dict_limitword.values())
        if syscontent.output_dict['(total)'] == 1:
            spamwriter_sum.writerow([str(e-num_err_txt)+'/'+str(e),num_txt_sat,num_user_list,w_limit_time,w_limit_place,s_limitword,s_num_limitword ]+list_sum_wst+list_result_sum)

        if syscontent.output_dict['(org)'] == 1:
            spamwriter.writerow([])
            spamwriter.writerow(['过滤词'.encode('gbk'),'词频'.encode('gbk')])
            for elem in list_filter:
                spamwriter.writerow([elem,dict_filter[elem]])
                #print elem,dict_filter[elem]

        try:
            fcDict['countfiles'] += 1
            #print str(os.getpid())+" : writing finish!......$"
            print "#TOIAL: "+ str(fcDict['countfiles']) + " complete!"
        except KeyError:
            print "Something wrong is counting files"
        return True,m_filename+'target.csv'


def mergeFiles_org(m_filename_list):
    #now = datetime.datetime.now()
    #str_now=now.strftime('%Y_%m_%d_%H_%M_%S')
    s=str(datetime.date.today())
    dir = os.path.dirname(m_filename_list[0])
    the_filename =dir+'/mergeFile_'+s+'.csv'
    with open(the_filename,'wb') as writefile:
        filewriter = csv.writer(writefile,dialect='excel')
        for e,filename in enumerate(m_filename_list):
            #print filename
            #print filename.encode('gbk')
            filereader = csv.reader(open(filename,'rb'),dialect='excel')
            if e ==0:
                 for row in filereader:
                    filewriter.writerow(row)
            else:
                 for i,row in enumerate(filereader):
                    if i>0:
                        filewriter.writerow(row)

    return the_filename


def mergeFiles(m_filename_list,match_str):
    #now = datetime.datetime.now()
    #str_now=now.strftime('%Y_%m_%d_%H_%M_%S')
    s=str(datetime.date.today())
    dir = os.path.dirname(m_filename_list[0])
    the_filename =dir+'/mergeFile_'+s+'.csv'
    with open(the_filename,'wb') as writefile:
        filewriter = csv.writer(writefile,dialect='excel')

        flag_utf8 = True
        e = 0
        for filename in m_filename_list:
            if re.search(match_str,filename):
                print filename.encode('gbk','ignore')
                filereader = csv.reader(open(filename,'rb'),dialect='excel')
                flist = filename.split("/")
                if e ==0:
                    e = 1
                    for j,row in enumerate(filereader):
                        if j == 0:
                            if chardet.detect(row[0])["encoding"]=="UTF-8-SIG":
                                str_file = flist[len(flist)-1]
                                row.insert(0,"文件名")
                                flag_utf8 = True
                            else:
                                str_file = flist[len(flist)-1].encode('gbk')
                                row.insert(0,"文件名".encode('gbk'))
                                flag_utf8 = False
                        if j > 0:
                            if flist:
                                row.insert(0,str_file)
                            else:
                                row.insert(0,filename)

                        filewriter.writerow(row)
                else:
                    for i,row in enumerate(filereader):
                        if i>0:
                            if flag_utf8:
                                str_file = flist[len(flist)-1]
                                row.insert(0,str_file)
                                filewriter.writerow(row)
                            else:
                                str_file = flist[len(flist)-1].encode('gbk')
                                row.insert(0,str_file)
                                filewriter.writerow(row)




    return the_filename

###################################################################
#@function 做关系图
#   @para  user  微博的作者
#          txt   微博的名称
#          mapwriter  打印微博的关系图
#   @return void
def create_map(user,txt,mapwriter):

    tms= r'//@(.*?):'
    t_user = re.findall(tms,txt,re.S)
    if t_user:
        mapwriter.writerow([user,t_user[0],1,0])

        k = 1
        while k < len(t_user):
            mapwriter.writerow([t_user[k-1],t_user[k],1,0])
            k +=1

    txt = re.sub(tms,"",txt)
    cms = r'@(.*?) '
    c_user = re.findall(cms,txt,re.S)
    for elem in c_user:
         mapwriter.writerow([user,elem,0,1])



#############################################################


def listToMatrix(list_filename):
     mdict = dict()
     list_elem = list()
     for filename in list_filename:
        mreader = csv.reader(open(filename,"rb"),dialect='excel')
        for e,elem in enumerate(mreader):
            if e>0:
                list_elem.append(elem)
                if not mdict.has_key(elem[0]):
                    mdict[elem[0]]=1
                if not mdict.has_key(elem[1]):
                    mdict[elem[1]]=1
     list_key = mdict.keys()
     for key in mdict:
        mdict[key] = [0]*len(list_key)
     for elem in list_elem:
        key1=elem[0]
        key2=list_key.index(elem[1])
        if elem[2] == "1":
            mdict[key1][key2] =2
        else:
            mdict[key1][key2] =1

     temp = list_filename[0].split('/')
     m_filename=temp[-1]
     print m_filename
     mwriter = csv.writer(open("/".join(temp[:-1]) + "/matrix_"+m_filename,"wb"),dialect='excel')
     mwriter.writerow([' ']+list_key)
     for elem in list_key:
        mwriter.writerow([elem]+mdict[elem])

def createMap(list_filename,col_id,col_text):
    m_file_path = ''
    for filename in list_filename:
        #print filename
        mreader = csv.reader(open(filename,"rb"),dialect='excel')
        temp = filename.split('/')
        m_filename=temp[-1]
        m_file_path = "/".join(temp[:-1]) + "/map_"+m_filename
        mwriter = csv.writer(open(m_file_path,"wb"),dialect='excel')
        mwriter.writerow(["用户A".encode("gbk"),"用户B".encode("gbk"),"转发".encode("gbk"),"评论".encode("gbk")])
        for e,row in enumerate(mreader):
            if e>0:
                create_map(row[int(col_id)],row[int(col_text)],mwriter)
    return m_file_path

#  if isinstance(elem, unicode):
