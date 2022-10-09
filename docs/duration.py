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
from xpinyin import Pinyin
from moviepy.editor import  VideoFileClip

''' 因为多次重复下载，而且又采用的H264 和 H265两种编码，导致同样内容的文件重复'''
''' 用过判定相同的时间，把文件名命名成相似的，方便人工对比'''
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

def GetVideoDuration():
    VideoDuration = {}
    FileList = os.listdir(SrcDir)
    
    for mp4 in FileList:
        Mp4Path = SrcDir + mp4 
        if ('.mp4' in Mp4Path) and (os.path.isfile(Mp4Path)):
            clip = VideoFileClip(Mp4Path)
            if clip.duration in VideoDuration.keys():
                VideoDuration[clip.duration].append(Mp4Path)
            else:
                VideoDuration[clip.duration] = [Mp4Path]
                
            print('%s---%s'%(Mp4Path, clip.duration))
            ''' 每次都要关掉，否则会报错 OS.Error'''
            clip.reader.close()
            clip.audio.reader.close_proc()
    return VideoDuration

def FindSameDurationFile():
    Durations = GetVideoDuration()
    for duration in Durations.keys():
        if len(Durations[duration]) > 1:
            prefix = str(duration).replace('.', '_') + '_'
            NumOfSame = len(Durations[duration])
            for num in range(0, NumOfSame):
                OldMp4Path = Durations[duration][num]
                sufix = '%02d' % num
                NewMp4Name = prefix + str(sufix) + '.mp4'
                Mp4Dir = '\\'.join(OldMp4Path.split('\\')[0:-1]) + '\\' 
                if os.path.exists(Mp4Dir):
                    Mp4Path = Mp4Dir + NewMp4Name
                else:
                    print('Dir not exists!:  %s' % Mp4Dir)
                    exit()
                
                ''' 多次运行之后，文件名可能已经存在，要处理掉，不能只考虑运行一次'''
                if os.path.exists(Mp4Path):
                    prefix = prefix + '_'
                    Mp4Path = '\\'.join(OldMp4Path.split('\\')[0:-1]) + prefix + NewMp4Name

                print('\t%s  -->   %s'% (OldMp4Path, Mp4Path))
                try:
                    shutil.move(OldMp4Path, Mp4Path)
                except:
                    print('\t\t%s  rename failed.....'%(OldMp4Path))
            print('------------------------------------------------------------')

FindSameDurationFile()


       


