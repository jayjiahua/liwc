#! /usr/bin/env python
#coding=utf-8

output_dict = {}

output_dict['(error)'] =1
output_dict['(import)'] =1
output_dict['(word)'] =1
output_dict['(total)'] =1
output_dict['(org)'] =1
output_dict['Export/splitwordCount.csv']=1

from multiprocessing import Value 

count_files  = Value('i',0)
splitwordCount = {}
'''
OUTPUT_ERROR = 1
OUTPUT_IMPORT = 1
OUTPUT_WORD = 1
OUTPUT_TOTAL = 1
OUTPUT_ORG = 1
'''