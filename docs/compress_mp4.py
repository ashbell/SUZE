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

Mp4Dir = []
def GetMp4Dir(path):
    FileList = os.listdir(path)
    for File in FileList:
        FilePath = path + File
        if os.path.isdir(FilePath):
            FilePath = FilePath +'\\'
            if (FilePath.split('\\')[-2] == 'mp4') :
                Mp4Dir.append(FilePath)
            GetMp4Dir(FilePath)



def IsWantToFind(mp4_path='', flag=''):
    mp4_root_dir = '\\'.join(mp4_path.split('\\')[0:-2]) + '\\'
    lst = os.listdir(mp4_root_dir)
    result = False
    for f in lst:
        if flag in f:
            result = True
    return result


def FindWantDir(flag=''):
    WannaDir = []
    GetMp4Dir(SrcDir)
    for path in Mp4Dir:
        if IsWantToFind(path, flag):
            mp4_root_dir = '\\'.join(path.split('\\')[0:-2]) + '\\'
            WannaDir.append(mp4_root_dir)
            ##print('%s ----> %s' %(mp4_root_dir, flag))
    
    return WannaDir

def IsMp4File(path):
    if os.path.isfile(path):
        return (path.split('.')[-1] == 'mp4')
    return False

    

def CompressMPEG4(dir_path):
    logfile = './compresslog'
    if os.path.exists(logfile):
        fd = open(logfile, 'a+', encoding='utf-8')
    else:
        fd = open(logfile, 'w+', encoding='utf-8')
    lst = os.listdir(dir_path)
    for f in lst:
        file_path = dir_path + f
        if ('concat_' in f) and (IsMp4File(file_path)):
            OutFile = dir_path + 'compressed_'  + str(random.randint(1000,9999)) + '.mp4'
            ''' Fuck chinese  align'''
            loginfo = '[ Convert - %s\t\t - %s ]' % (file_path,OutFile) 
            print(loginfo)
            cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -c:v libx264 -acodec  copy  -crf 20 -preset:v veryslow %s' \
                    % (file_path, OutFile)
            os.system(cmd)

            fd.write(loginfo + '\n')
            print('[ Delete - %s ]' % (file_path) )
            os.unlink(file_path)
            ##input('>>')
    fd.close()        

        
Dirs = FindWantDir('concat_')
for path in Dirs:
    CompressMPEG4(path)
