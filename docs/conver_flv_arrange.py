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


## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')

bash_path = "C:\\cygwin64\\bin\\mintty.exe"
ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"


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

flvs = []

def  find_spec_file_path(path, file_type=''):
    lst = os.listdir(path)
    for f in lst:
        file_path = path + f 
        if os.path.isdir(file_path):
            file_path  = file_path + '\\'
            find_spec_file_path(file_path, file_type)
        elif os.path.isfile(file_path):
            if file_type == file_path[-4:]:
                flvs.append(file_path)



def GetMediaInfo(path, info=''):
    result = ''
    legal = ['duration', 'codec_name', 'width', 'height', 'codec_type'] 

    if not (info in legal):
        print('Invalid para. GetMediaInfo: %s-%s' %(path, info))
        ##exit()

    if mu.acquire(True):
        cmd = 'ffprobe -v quiet -show_streams -print_format json %s' % path 
        output = subprocess.getoutput(cmd)
        output = output.replace('Active code page: 65001', '')
        json_data = json.loads(output)
    mu.release()
        
    
    if not 'streams' in json_data:
        print('Get Media info Failed :%s' % path)
        result = 'None'
    else:
        try:
            result =  (json_data['streams'][0][info])
        except:
            result = 'None'
    return result

def  convert_file(path, src_type = '', dst_type=''):
    ''' Convet src file media type to dst type'''
    if (src_type == 'flv' and dst_type == 'mp4') and \
                                os.path.exists(path):
        file_dir = '\\'.join(path.split('\\')[0:-1]) + '\\'
        file_name = path.split('\\')[-1:][0]
        tmp = list(file_name)
        tmp[-1] = '4'
        tmp[-2] = 'p'
        tmp[-3] = 'm'
        tmp[-4] = '.'
        dst_file_name = ''.join(tmp)
        dst_file = file_dir + dst_file_name
        if os.path.exists(dst_file):
            dst_file = file_dir + 'exists_'+str(random.randint(100,999)) + '_'+dst_file_name

        """ method 1
        cmd1 = 'ffmpeg -hide_banner -v  quiet -stats -i %s -ar 44100 -ac 2 -vcodec copy %s' \
                %(path, dst_file)
        print('Convert - %s ->  %s ' %(path, dst_file))
        ##os.system(cmd1)
        """
        
        print('Convert - %s ->  %s ' %(path, dst_file))
        p =  subprocess.Popen([bash_path, ffmpeg_path, "-hide_banner", "-i", path, "-ar", "44100", \
                                                   "-ac", "2", "-vcodec", "copy", dst_file ], \
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read() 

        
        ''' check dst file is ok?'''
        if (GetMediaInfo(dst_file, 'codec_type') == 'video'):
            print('Conver - OK, Delete Src! %s' % path)
            os.unlink(path)
        else:
            print('Not sure What Fucking happend in dst file: %s' % dst_file)
        
threads = []
mu  = threading.Lock()
find_spec_file_path(SrcDir, '.flv')
for flv in flvs:
    t = threading.Thread(target = convert_file, args=[flv, 'flv', 'mp4'])
    threads.append(t)


for t in threads:
    t.setDaemon(True)
    t.start()

    while True:
        if (len(threading.enumerate()) < 4):
            break

for t in threads:
    t.join()


            




