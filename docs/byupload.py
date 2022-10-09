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


''' 自动上传到百度网盘, 自动寻找已经压缩好的目录，上传文件，./bdupload.py  path '''
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

upload_info = {}
def get_compressed_mp4_path(path=''):
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            file_path  = path + f
            if os.path.isdir(file_path):
                file_path = file_path + '\\'
                get_compressed_mp4_path(file_path)
            elif os.path.isfile(file_path)  and ('mp4' in file_path) \
                   and ('.mp4' in file_path):
                author = file_path.split('\\')[-2:-1][0]
                ##print('Found   -  %-15s  -  %s' % (author, file_path))
                if author in upload_info.keys():
                    upload_info[author].append(file_path)
                else:
                    upload_info[author] = [file_path]
            else:
                pass

print('Scan - Compressed mp4 ......')
get_compressed_mp4_path(SrcDir)
print(upload_info)

log_file = './uplog'
if os.path.exists(log_file):
    fd =open(log_file, 'w+', encoding='utf-8')
else:
    fd =open(log_file, 'a+', encoding='utf-8')

for author in upload_info.keys():
    mp4_files = upload_info[author]
    for mp4 in mp4_files:
        TimeNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info = '%s: %s - %s > START!!!!!!!!!!!!!!!!!!!!!\n' %(TimeNow, author, mp4)
        fd.write(info)
        print('Up - %s -->  %s' %(author, mp4))
        cmd_mkdir = 'bypy -q mkdir %s' % author
        os.system(cmd_mkdir)
        time.sleep(3)
        cmd_up = 'bypy -q upload %s  %s ' % (mp4, author+'/')
        os.system(cmd_up)
        TimeNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info = '%s: %s - %s > END!!!!!!!!!!!!!!!!!!!!!!!!!\n' %(TimeNow, author, mp4)
        fd.write(info)
        fd.write('\n')
fd.close()
                
    
