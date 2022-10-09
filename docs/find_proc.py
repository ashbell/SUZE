#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import re
import base64
import shutil
import subprocess
import time
import wget
import threading
import urllib.request
import codecs
import re
import random
import datetime
from xpinyin import Pinyin
from moviepy.editor import  VideoFileClip
from moviepy.editor import *
from pymediainfo import MediaInfo
from pprint import pprint


''' 寻找给定目录下  需要处理的所有子目录 ./find_proc.py     path '''
## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')


##SrcDir = 'E:\\VC-短视频主播\\W\\W微笑沉静2\\mp4\\'
##SrcDir = 'E:\\VC-短视频主播\\Y\\Y云飞\\mp4\\A\\'
'''/cygdrive/e/VC-短视频主播/Y/Y云姐/mp4'''
if len(sys.argv) > 1:
    path = sys.argv[1].split('/')[2:]
    path[0] = (path[0]+':').upper()
    PyPath = '\\'.join(path)
else:
    print('Argv  Path  is need!')
    exit()

if PyPath[-1] != '\\':
    PyPath = PyPath + '\\'

SrcDir = PyPath

search_result = []
def search_spec_flag(path='', search_flag=''):
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            file_path  = path + f
            if os.path.isdir(file_path):
                file_path = file_path + '\\'
                search_spec_flag(file_path, search_flag)
            elif os.path.isfile(file_path)  and (search_flag in file_path) \
                   and ('.txt' in file_path):
                search_result.append(file_path)
            else:
                pass

print('Scan - Specify flag........')
search_spec_flag(SrcDir, 'proc')

for f  in search_result:
    proc_dir = '\\'.join(f.split('\\')[0:-1])
    if os.path.isdir(proc_dir)  and \
            os.path.exists(proc_dir):
        proc_dir = proc_dir + '\\'
        size = subprocess.check_output(['du', '-s', proc_dir]).split()[0].decode('utf-8')
        size = int(size)
        if size  >  20*1000:
            print('%s - %s' %(proc_dir, size))



        
    
