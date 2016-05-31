#!/usr/bin/env python 
#coding=utf-8     
import Tkinter as tk 
import ttk
import tkFileDialog    
import tkMessageBox

import test1 as T
import city 
import nlpir as N
import datetime
import time
import os
import syscontent
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
#seg= SEG()

singleWordCount={} #记录字频
wordCountDict={}  #记录词频
worddict={}
classdict={}
word_pr_dict={} #精确的词典
dict_classname={}

loc_userdict='Import/userDict.txt'
loc_worddict="Import/word.csv"
loc_classdict="Import/class.csv"
loc_wordCount="Export/wordCount.csv"
loc_singleWordCount="Export/singlewordCount.csv"
loc_splitwordCount="Export/splitwordCount"

optionList = ('*','2014', '2013','2012','2011','2010','2009','2015','2016')
optionList1 =('*','1', '2','3','4','5','6','7','8','9','10','11','12')
optionList2 =('*','1', '2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19',
'20','21','22','23','24','25','26','27','28','29','30','31')
optionList_city=('*') 
m_filename=""

class Application(tk.Frame):
        
                  
    def __init__(self, master=None):
        tk.Frame.__init__(self, master,)   
        self.grid(row=0, column=0,sticky=tk.N+tk.S+tk.E+tk.W) 
        #self.grid_propagate(0)     
        self.flag_placeMan = False
        self.flag_dateMan = False                      
        self.createWidgets()
        self.list_files=list()
        
        if not N.Init('',N.ENCODING.UTF8_CODE,''):          
            print("Initialization failed!")
            exit(-111111)
        N.mImportUserDict('Import/userDict.txt')
        T.init_dict(worddict,classdict,dict_classname,word_pr_dict,wordCountDict,singleWordCount)
        T.init_output()
        
   
    

    def createWidgets(self):
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        #top.geometry('600x400')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1) 
        
        
        #菜单栏
        top = self.winfo_toplevel()
        self.menuBar = tk.Menu(top)
        top['menu'] = self.menuBar
        self.subMenu = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='文件', menu=self.subMenu)
        self.subMenu.add_command(label='打开', command=self.__openFileHandler)
        self.subMenu.add_command(label='其他功能', command=self.__openManyFileHandler)
        self.subMenu.add_command(label='批量合并(total)', command=self.__openManyFileHandler_total)
        self.subMenu.add_command(label='批量处理载入', command=self.__openManyFileAnalyzer)
        self.subMenu2 = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='词典选项', menu=self.subMenu2)
        self.subMenu2.add_command(label='更新用户词典',command=self.__updateUserDictHandler)
        self.subMenu2.add_command(label='导入词典(类-词list)',command=self.__importDictHandler)
        self.subMenu2.add_command(label='导出词典(按类别)',command=self.__exportDictHandler)
        self.subMenu3 = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='输出文件设置', menu=self.subMenu3)
        self.subMenu3.add_command(label='设置提示',command=self.__outputInfo)
        #self.subMenu3.add_command(label='设置完成',command=self.__outputFinish)
        self.subMenu4 = tk.Menu(self.menuBar)
        self.menuBar.add_cascade(label='社会网络分析', menu=self.subMenu4)
        self.subMenu4.add_command(label='邻接表转为邻接矩阵',command=self.__listToMatrix)
        self.subMenu4.add_command(label='制作网络表',command=self.__createMap)
        
        
        
        
        #notice 第0行，中
        self.txt_notice = tk.Label(self,text="请输入关键词, +表示关键词的合取， |表示析取")
        self.txt_notice.grid(row=0 , column=3) 
        
        
        self.txt_block1 = tk.Label(self,width=2)
        self.txt_block1.grid(row=0 , column=0)
        
        self.txt_block2 = tk.Label(self,width=1)
        self.txt_block2.grid(row=0 , column=2)
        
        self.txt_block3 = tk.Label(self,width=1)
        self.txt_block3.grid(row=0 , column=4)
         
        self.txt_block4 = tk.Label(self,width=2)
        self.txt_block4.grid(row=0 , column=6)
        
        ####
        
        self.txt_block5 = tk.Label(self)
        self.txt_block5.grid(row=2 , column=0)
        
        self.txt_block6 = tk.Label(self)
        self.txt_block6.grid(row=4 , column=0)
        
        self.txt_block7 = tk.Label(self)
        self.txt_block7.grid(row=6 , column=0)
        
        self.txt_block8 = tk.Label(self)
        self.txt_block8.grid(row=8 , column=0)
        
        
        
                          
        
        #text   第一行，左   
        self.lable1 = tk.Label(self,text="输入：")
        self.lable1.grid(row=1,column=1)
        
        #entry   第一行，中
        self.var_input_word = tk.StringVar()
        self.labelframe13 = tk.LabelFrame(self)
        self.labelframe13.grid(row=1,column =3)
        self.entry = tk.Entry(self.labelframe13, width=62,textvariable=self.var_input_word)
        self.entry.grid(row=0,column =1)
        self.var_exact = tk.IntVar()
        self.cbt_exact = tk.Checkbutton(self.labelframe13,text="精确",variable= self.var_exact)
        self.cbt_exact.grid(row=0,column =2)
        #self.entry.grid(row=1,column=3,sticky=tk.E+tk.W)
        #self.entryScroll = tk.Scrollbar(self, orient=tk.HORIZONTAL,command=self.__scrollHandler)
        #self.entryScroll.grid(row=2, sticky=tk.E+tk.W)
        #self.entry['xscrollcommand'] = self.entryScroll.set
        
        #button   第一行，由
        self.bt_search =tk.Button(self, text='搜索统计', width=10 ,command=self.__textHandler)
        self.bt_search.grid(row=1, column=5)#,sticky=tk.N+tk.S+tk.E+tk.W)
        
        self.bt_search_all =tk.Button(self, text='批量处理', width=10 ,command=self.__alltextHandler)
        #self.bt_search.grid(row=1, column=5)#,sticky=tk.N+tk.S+tk.E+tk.W)
                        
        
        #第三行
        self.lable2 = tk.Label(self,text="限制选项：")
        self.lable2.grid(row=3,column=1)
        
        self.labelframe = tk.LabelFrame(self, text="Choice")
        self.labelframe.grid(row=3, column=3,columnspan=2)
         
        self.left = tk.Label(self.labelframe, text="起始:")
        self.left.grid(row=0, column=0)
        
        
        ##
        self.var_year = tk.StringVar()
        self.var_year.set(optionList[0])
        
        self.var_month = tk.StringVar()
        self.var_month.set(optionList1[0])

        self.var_day = tk.StringVar()
        self.var_day.set(optionList2[0])
        
        
        self.om = tk.OptionMenu(self.labelframe, self.var_year, *optionList)        
        self.om.grid(row=0, column=1)
        self.mlable1 = tk.Label(self.labelframe,text='年')
        self.mlable1.grid(row=0, column=2)
        self.mlable2 = tk.Label(self.labelframe,text='月')
        self.mlable2.grid(row=0, column=4)
        self.mlable3 = tk.Label(self.labelframe,text='日   至：')
        self.mlable3.grid(row=0, column=6)
        
        self.om2 = tk.OptionMenu(self.labelframe, self.var_month, *optionList1)        
        self.om2.grid(row=0, column=3)
        self.om3 = tk.OptionMenu(self.labelframe, self.var_day, *optionList2)        
        self.om3.grid(row=0, column=5)
        
        
        
        #self.labelframe1 = tk.LabelFrame(self)
        #self.labelframe1.grid(row=5, column=3)
                
        #self.left1 = tk.Label(self.labelframe1, text="至:")
        #self.left1.grid(row=0, column=0)
        
        self.var_year1 = tk.StringVar()
        self.var_year1.set(optionList[0])
               
        self.var_month1 = tk.StringVar()
        self.var_month1.set(optionList1[0])
        
        self.var_day1 = tk.StringVar()
        self.var_day1.set(optionList2[0])
               
               
        self.om1 = tk.OptionMenu(self.labelframe, self.var_year1, *optionList)        
        self.om1.grid(row=0, column=7)
        self.mlable11 = tk.Label(self.labelframe,text='年')
        self.mlable11.grid(row=0, column=8)
        self.mlable21 = tk.Label(self.labelframe,text='月')
        self.mlable21.grid(row=0, column=10)
        self.mlable31 = tk.Label(self.labelframe,text='日')
        self.mlable31.grid(row=0, column=12)
               
        self.om21 = tk.OptionMenu(self.labelframe, self.var_month1, *optionList1)        
        self.om21.grid(row=0, column=9)
        self.om31 = tk.OptionMenu(self.labelframe, self.var_day1, *optionList2)        
        self.om31.grid(row=0, column=11)
        
        
        self.labelframe35 = tk.LabelFrame(self,text="choice")
        self.labelframe35.grid(row=3, column=5)
        self.bt_dateChoose = tk.Button(self.labelframe35,text="手动输入",command=self.__onChooseDate)
        self.bt_dateChoose.grid(row=0, column=0)
        self.bt_clearPlace = tk.Button(self.labelframe35,text="clear",command=self.__onClearDate)
        self.bt_clearPlace.grid(row=0, column=1)
        
        
        
        self.labelframe_man = tk.LabelFrame(self,text="Choice")
        #self.labelframe.grid(row=3, column=3,columnspan=2)
        self.mlable1_man = tk.Label(self.labelframe_man,text='-')
        self.mlable1_man.grid(row=0, column=2)
        self.mlable2_man = tk.Label(self.labelframe_man,text='-')
        self.mlable2_man.grid(row=0, column=4)
        self.mlable3_man = tk.Label(self.labelframe_man,text='   至：')
        self.mlable3_man.grid(row=0, column=6)
        self.et_date = tk.Entry(self.labelframe_man,textvariable=self.var_day,width=6)
        self.et_date.grid(row=0,column=5)
        self.et_month = tk.Entry(self.labelframe_man,textvariable=self.var_month,width=6)
        self.et_month.grid(row=0,column=3)
        self.et_year = tk.Entry(self.labelframe_man,textvariable = self.var_year,width=10)
        self.et_year.grid(row=0,column=1)
        
        self.mlable4_man = tk.Label(self.labelframe_man,text='-')
        self.mlable4_man.grid(row=0, column=8)
        self.mlable5_man = tk.Label(self.labelframe_man,text='-')
        self.mlable5_man.grid(row=0, column=10)
        self.et_date1 = tk.Entry(self.labelframe_man,textvariable=self.var_day1,width=6)
        self.et_date1.grid(row=0,column=11)
        self.et_month1 = tk.Entry(self.labelframe_man,textvariable=self.var_month1,width=6)
        self.et_month1.grid(row=0,column=9)
        self.et_year1 = tk.Entry(self.labelframe_man,textvariable = self.var_year1,width=10)
        self.et_year1.grid(row=0,column=7)
        
        
        
        
        
        
        #第五行
        self.labelframe1 = tk.LabelFrame(self, text="省市")
        self.labelframe1.grid(row=5, column=3,columnspan=2)
                 
        self.left1 = tk.Label(self.labelframe1, text="prov:")
        self.left1.grid(row=0, column=0)
        
        self.var_province = tk.StringVar()
        self.var_province.set(optionList[0])
                       
        self.var_city = tk.StringVar()
        self.var_city.set(optionList1[0])
        
        
        self.labelframe55 = tk.LabelFrame(self,text="choice")
        self.labelframe55.grid(row=5, column=5)
        self.bt_placeChoose = tk.Button(self.labelframe55,text="手动输入",command=self.__onChoosePlace)
        self.bt_placeChoose.grid(row=0, column=0)
        self.bt_clearPlace = tk.Button(self.labelframe55,text="clear",command=self.__onClearPlace)
        self.bt_clearPlace.grid(row=0, column=1)
        
        
        
        self.omp = tk.OptionMenu(self.labelframe1, self.var_province, *optionList_prov)
        self.omp.grid(row=0, column=1)
        
        #self.omp = tk.OptionMenu(self.labelframe1, self.var_city, *optionList_city)
        self.left2 = tk.Label(self.labelframe1, text="city:")
        self.left2.grid(row=0, column=2)
        
        #self.omc = tk.Button(self.labelframe1,text= '*' ,command=self.__onChoose ,width=8) 
        #self.omc.grid(row=0, column=3)
        self.omc_new = tk.OptionMenu(self.labelframe1, self.var_city, *optionList_city)
        self.omc_new.grid(row =0,column = 3)
        
        
        self.omre = tk.Button(self.labelframe1,text= '重置' ,command=self.__onReset ,width=8) 
        self.omre.grid(row=0, column=4)
        
        
        
        self.labelframe1_man = tk.LabelFrame(self, text="省市")
        self.left1_man = tk.Label(self.labelframe1, text="province:")
        self.left1_man.grid(row=0, column=0)
        self.et_prov=tk.Entry(self.labelframe1_man,textvariable = self.var_province)
        self.et_prov.grid(row=0,column=1)
        self.mid_man = tk.Label(self.labelframe1_man,text=" city:")
        self.mid_man.grid(row=0,column=2)
        self.et_city = tk.Entry(self.labelframe1_man,textvariable = self.var_city)
        self.et_city.grid(row=0,column=3)
        
        
        
        
        #第七行
        self.lable3 = tk.Label(self,text="文件位置：")
        self.lable3.grid(row=7,column=1)
        
        self.var_file_loc =  tk.StringVar()
        #self.var_file_loc.set('""')
        self.file_location = tk.Label(self,text="none",textvariable = self.var_file_loc)
        self.file_location.grid(row=7,column=3)
        
        self.var_msg = tk.StringVar()
        self.lableMeg = tk.Label(self,text='已成功载入字典',bg='green',textvariable = self.var_msg)
        self.var_msg.set('已成功载入字典')
        self.lableMeg.grid(row = 7 , column = 5)
    
    def __updateUserDictHandler(self):
        N.mImportUserDict(loc_userdict)
    
    
    def __onChooseDate(self):
        if not self.flag_dateMan:
             self.labelframe.grid_remove()
             self.flag_dateMan = True
             self.labelframe_man.grid(row=3,column = 3)
             self.bt_dateChoose['text'] = '选项'
        else:
            self.labelframe.grid()
            self.flag_dateMan= False
            self.labelframe_man.grid_remove()
            self.bt_dateChoose['text'] = '手动输入'
        
    def __onClearDate(self):
        self.var_day.set('*')
        self.var_month.set('*')
        self.var_year.set('*')
        self.var_day1.set('*')
        self.var_month1.set('*')
        self.var_year1.set('*')
        
    
    def __onClearPlace(self):
        self.var_city.set('*')
        self.var_province.set('*')
    
    def __onChoosePlace(self):
        if not self.flag_placeMan:
            self.labelframe1.grid_remove()
            self.flag_placeMan = True
            self.bt_placeChoose['text'] = '选项'
            self.labelframe1_man.grid(row=5,column = 3)
        else:
            self.flag_placeMan = False
            self.labelframe1.grid()
            self.bt_placeChoose['text'] = '手动输入'
            self.labelframe1_man.grid_remove()
        
    def __onReset(self):
        province=self.var_province.get()
        if province !='*':
            for k,v in city.PROVINCE:
                if v == province:
                    id = k
                    break
            
            optionList_city = city.CITY[id]
            list_city=list()
            for k,v in optionList_city:
                list_city.append(v)
            optionList_city = tuple(list_city)
            #self.omc_new = tk.OptionMenu(self.labelframe1, self.var_city, *optionList_city)
            #self.omc_new.grid(row =0,column = 3)
            self.omc_new.grid_remove()
            self.omc_new = tk.OptionMenu(self.labelframe1, self.var_city, *optionList_city)
            self.omc_new.grid(row =0,column = 3)
        #self.var_province.set('*')
        self.var_city.set('*')
            
        
    
    def __openFileHandler(self):
        m_filename=tkFileDialog.askopenfilename(title='请选择处理的文档',filetypes=[("CSV","*.csv")])
        self.var_file_loc.set(m_filename)
        self.var_msg.set('已载入文件')
        print '__openFileHandler :'+m_filename.encode('gbk')
    
    
    
    ###########################################################################################################################
    
    #批量合并    
    def __openManyFileHandler(self):
        m_filename_list=tkFileDialog.askopenfilenames(title='请选择处理的文档',filetypes=[("CSV","*.csv")])
        if m_filename_list !=None and m_filename_list!=[] and m_filename_list!="":
            
            """
            self.var_file_loc.set('待文件处理数量为：'+str(len(m_filename_list)))
            self.var_msg.set('正在合并文件....')
            self.lableMeg['bg']='red'
            self.lableMeg.update()
        
            #print m_filename_list
        
            m_filename_merge=T.mergeFiles_org(m_filename_list)
        
            self.var_msg.set('完成合并')
            self.lableMeg['bg']='yellow'
            self.lableMeg.update()
            self.var_file_loc.set(m_filename_merge)
            """
            import csv
            import datetime
            f_header = ["ID","用户名".encode('gbk'),"链接".encode('gbk'),"内容".encode('gbk'),"时间".encode('gbk'),"转发".encode('gbk'),"评论".encode('gbk'),"赞".encode('gbk'),
                "性别".encode('gbk'),"地区".encode('gbk'),"描述".encode('gbk'),"是否认证".encode('gbk'),"关注".encode('gbk'),"粉丝".encode('gbk'),
                "微博".encode('gbk'),"标签".encode('gbk')]
                            
            for mfile in m_filename_list:
                thereader=csv.reader(open(mfile,"rb"),dialect='excel')
                mdict={}
                row = mfile.split("_")[1]
                pro = mfile.split("_")[2]
                
                for e,elem in enumerate(thereader):
                    if e>0:
                        k = elem[4].split(" ")[0]
                        mdict[k]=list()
                thereader=csv.reader(open(mfile,"rb"),dialect='excel')
                for e,elem in enumerate(thereader):
                    if e>0:
                        k = elem[4].split(" ")[0]
                        mdict[k].append(elem)
                
                
                #print mdict
                keylist = mdict.keys()
                for e,key in enumerate(keylist):
                    #if e < len(keylist) -1:
                    date1=key
                    mdate=datetime.datetime.strptime(date1,"%Y-%m-%d") +datetime.timedelta(days=1)
                    date2=mdate.strftime("%Y-%m-%d")
                    
                    mwriter = csv.writer(open("result_"+row+"_"+pro+"_"+date1+"_"+date2+".csv",'wb'),dialect='excel')
                    mwriter.writerow(f_header)
                    #print mdict[key]
                    for col in mdict[key]:
                        mwriter.writerow(col)
                    
                       
            
            
    #批量合并 total
    def __openManyFileHandler_total(self):
           import tkSimpleDialog
           ms=tkSimpleDialog.askstring(title = '输入对话',prompt = '请输入需要合并的文件匹配字符串，如total')
           if ms == None:
               return  
           m_filename_list=tkFileDialog.askopenfilenames(title='请选择处理的文档',filetypes=[("CSV","*.csv")])
           if m_filename_list !=None and m_filename_list!=[] and m_filename_list!="":
               self.var_file_loc.set('待文件处理数量为：'+str(len(m_filename_list)))
               self.var_msg.set('正在合并文件....')
               self.lableMeg['bg']='red'
               self.lableMeg.update()
           
           
               m_filename_merge=T.mergeFiles(m_filename_list,ms)
           
               self.var_msg.set('完成合并')
               self.lableMeg['bg']='yellow'
               self.lableMeg.update()
               self.var_file_loc.set(m_filename_merge)
    
    #批量处理文件载入
    def __openManyFileAnalyzer(self):
        m_filename_list=tkFileDialog.askopenfilenames(title='请选择处理的文档',filetypes=[("CSV","*.csv")])
        if m_filename_list !=None and m_filename_list!=[] and m_filename_list!="":
           
            
            num_file = len(m_filename_list)
            self.var_file_loc.set('待文件处理数量为：'+str(len(m_filename_list)))
            self.list_files = m_filename_list
        
            self.bt_search_all.grid(row=1, column=5)
            self.bt_search.grid_remove()

    #批量处理    
    def __alltextHandler(self):
        keyword = self.var_input_word.get()
        keyword_gbk = keyword.encode('gbk')
        
        list_limited = list()
        list_limited.append(self.var_province.get())
        list_limited.append(self.var_city.get())
                    
        list_limited.append(self.var_year.get())
        list_limited.append(self.var_month.get())
        list_limited.append(self.var_day.get())
        list_limited.append(self.var_year1.get())
        list_limited.append(self.var_month1.get())
        list_limited.append(self.var_day1.get())
        
        
        list_file = list(self.list_files)
        from multiprocessing import Pool,Manager,Value 
        import itertools
        import syscontent
        #syscontent.count_files.value = 0
        
        pool = Pool()
        manager = Manager()
        wcDict = manager.dict(wordCountDict)
        
        fcDict = manager.dict()
        fcDict['countfiles'] = 0
        
        ###2015.1.13 用于存储分词词频的值
        if os.path.exists(loc_splitwordCount+'.csv') and syscontent.output_dict['Export/splitwordCount.csv'] == 1:
            splitwcDict = manager.dict(T.init_spiltwcDict(loc_splitwordCount+'.csv'))
        else:
            splitwcDict = manager.dict()
        splitwcDict_empty = manager.dict()
        
        print "Going to divide the task....."
        resuls =pool.map(T.wrap_txtAnalyze,itertools.izip(itertools.repeat(splitwcDict),itertools.repeat(splitwcDict_empty),itertools.repeat(fcDict),itertools.repeat(singleWordCount),itertools.repeat(wcDict),itertools.repeat(worddict),itertools.repeat(classdict),itertools.repeat(dict_classname),itertools.repeat(word_pr_dict),list_file,itertools.repeat(keyword),itertools.repeat(list_limited),itertools.repeat(self.var_exact.get())))
        pool.close()
        pool.join()
        
       
        #因为wcDict是Manager()的附属，不能直接对它写入文件，所以创建wcd副本
        wcd = dict(wcDict)    
        T.saveWordCount(wcd,dict(),loc_wordCount,["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
        
        splitwcd = dict(splitwcDict)
        splitwcd_empty = dict(splitwcDict_empty)
        T.saveWordCount(splitwcd,splitwcd_empty,loc_splitwordCount+".csv",["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
        
        #T.saveWordCount(singleWordCount,loc_singleWordCount,["字".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
        self.bt_search.grid()
        self.bt_search_all.grid_remove()   
        
    #单个文件处理
    def __textHandler(self):
        keyword = self.var_input_word.get()
        keyword_gbk = keyword.encode('gbk')
        #print keyword_gbk
        op_filename=self.var_file_loc.get()
        if self.var_file_loc.get()=="":
            
            tkMessageBox.showinfo('注意','没有文件')
        else:
            
            list_limited = list()
            list_limited.append(self.var_province.get())
            list_limited.append(self.var_city.get())
            
            list_limited.append(self.var_year.get())
            list_limited.append(self.var_month.get())
            list_limited.append(self.var_day.get())
            list_limited.append(self.var_year1.get())
            list_limited.append(self.var_month1.get())
            list_limited.append(self.var_day1.get())
            
            
            
            self.var_msg.set('正在处理中....')
            self.lableMeg['bg']='red'
            self.lableMeg.update()
            
            fcDict =dict()
            fcDict['countfiles'] = 0
            m_wordCountDict = dict(wordCountDict)
            splitwcDict = dict()
            splitwcDict_empty = dict()
            mflag,msg=T.txtAnalyze(splitwcDict,dict(),splitwcDict_empty,singleWordCount,m_wordCountDict,worddict,classdict,dict_classname,word_pr_dict,op_filename,keyword,list_limited,self.var_exact.get())
            if mflag:                
                #T.gbk2utf8(gbk_filename)
                T.saveWordCount(m_wordCountDict,dict(),loc_wordCount,["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
                T.saveWordCount(splitwcDict,splitwcDict_empty,loc_splitwordCount+".csv",["词".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
                #T.saveWordCount(singleWordCount,loc_singleWordCount,["字".encode('gbk'),datetime.datetime.now(),"总计".encode('gbk')])
                self.var_msg.set('已完成')
                self.lableMeg['bg']='yellow'
                self.lableMeg.update()
            else:
                for elem in wordCountDict:
                    wordCountDict[elem] = 0
                for elem in singleWordCount:
                    singleWordCount[elem] = 0
                tkMessageBox.showinfo('错误_文件占用',msg)
                self.var_msg.set('准备就绪')
                self.lableMeg['bg']='green'
                self.lableMeg.update()
                
    #导入字典（类别：词）            
    def __importDictHandler(self):
        m_newDict=tkFileDialog.askopenfilename(title='请选择导入的词典（类-词list）',filetypes=[("CSV","*.csv")])
        if m_newDict:
            T.importDict(m_newDict,worddict,classdict,dict_classname,loc_worddict,loc_classdict)
        import tkMessageBox
        
    #导出字典（类别：词）     
    def __exportDictHandler(self):
        import tkSimpleDialog
        import tkMessageBox
        ks=tkSimpleDialog.askstring(title = '输入对话',prompt = '请输入导出的类别（名称），如高兴')
        mfileloc=tkFileDialog.asksaveasfilename(title='请选择保存的路径与名称',filetypes=[("CSV","*.csv")])
        if ks !=None and mfileloc!=None and mfileloc!="":
            print 'Export path: '+mfileloc.encode('gbk')
            print 'Export class: '+ks.encode('gbk')
            if T.exportDictHandler(ks.encode('gbk'),dict_classname,worddict,mfileloc.encode('gbk')):
                tkMessageBox.showinfo("消息", "导出成功")    
            else:
                tkMessageBox.showinfo("消息", "导出失败（没有该类别）")    
                       
    def __outputInfo(self):
        tkMessageBox.showinfo("提示", "请在/Import/outputFilesSelection.csv下设置") 
    def __outputFinish(self):
        T.init_output()      
    
    #邻接表转为邻接矩阵
    def __listToMatrix(self):
        m_filename_list=tkFileDialog.askopenfilenames(title='请选择转换的文档',filetypes=[("CSV","*.csv")])
        if m_filename_list !=None and m_filename_list!=[] and m_filename_list!="":
            T.listToMatrix(m_filename_list)
        tkMessageBox.showinfo("提示", "已完成转换")
    def __createMap(self):
        import tkSimpleDialog
        m_filename_list=tkFileDialog.askopenfilenames(title='请选择制作关系图的文档',filetypes=[("CSV","*.csv")])
        col_id=tkSimpleDialog.askstring(title = '输入对话',prompt = '请输入处理文件【用户ID】所在的列数(数字，从0开始计数)')
        if col_id == None:
            return
        col_text=tkSimpleDialog.askstring(title = '输入对话',prompt = '请输入处理文件【文本】所在的列数(数字，从0开始计数)')
        if col_text == None:
            return
        if m_filename_list !=None and m_filename_list!=[] and m_filename_list!="":
            T.createMap(m_filename_list,col_id,col_text)
        tkMessageBox.showinfo("提示", "已完成制作")
        
                                            
if __name__ == '__main__':            
    list_province = list()
    for k,v in city.PROVINCE:
        list_province.append(v)
    optionList_prov = tuple(list_province)
                                        

    app = Application()                       
    app.master.title('文本分析程序')    
    app.mainloop()                       

#self.mycanvas= tk.Canvas(self)
#self.mycanvas.grid(row=0, column=1)


        
'''
       i=1
       for op_filename in self.list_files:
           self.var_file_loc.set(op_filename)
           self.var_msg.set('正在处理中'+str(i)+'/'+str(len(self.list_files))+'......')
           self.lableMeg['bg']='red'
           self.lableMeg.update()
           
           try:
                     
               mflag,msg=T.txtAnalyze(singleWordCount,wordCountDict,worddict,classdict,dict_classname,word_pr_dict,op_filename,keyword,list_limited,self.var_exact.get())
               if mflag:                                        
                   self.var_msg.set('已完成'+str(i)+'/'+str(len(self.list_files)))
                   self.lableMeg['bg']='yellow'
                   self.lableMeg.update()
               else:
                   tkMessageBox.showinfo('错误_文件占用',msg)
                   self.var_msg.set('准备就绪')
           except (Exception),err:
               print "aaaaaaaaaaaaaaaaa!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"     
                   
           i=i+1
       '''

