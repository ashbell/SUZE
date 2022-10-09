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
import mimetypes
##import magic
import easyocr
import cv2


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

RecordDir = ''
ProductDir = ''

''' MP4 文件必须放在子目录，参数传递为父目录，否则无法识别，没精力去做路径识别 '''

def IsVideoFile(path):
    ftype = mimetypes.guess_type(path)
    if 'mp4' in ftype[0]:
        return True
    else:
        return False

def MoveRecordToDir(path, dst_path):
    ''' 把录屏文件移动到其他地方 '''
    pass


def MoveProductToDir(path, dst_path):
    ''' 把产品文件移动到其他地方 '''
    pass

def DetectTextFromImage(path):
    reader = easyocr.Reader(['ch_sim','en'], gpu=False)
    with open(path, 'rb') as f:
        img = f.read()
        result = reader.readtext(img)

        for res in result:
            pass
        ##print ('%s--%s' %(result[0][1], result[0][2]))
        return result


def GetMediaInfo(path, info=''):
    legal = ['duration', 'codec_name', 'width', 'height'] 

    if not (info in legal):
        print('Invalid para. GetMediaInfo: %s-%s' %(path, info))
        exit()
    cmd = 'ffprobe -v quiet -show_streams -print_format json %s' % path 
    output = subprocess.getoutput(cmd)
    output = output.replace('Active code page: 65001', '')
    json_data = json.loads(output)
    if not 'streams' in json_data:
        print('Get Media info Failed')
        exit()
    else:
        return (json_data['streams'][0][info])
     

def ReadTextFromMiddleCrop(frameimg1 = '', frameimg2=''):
    ''' 第一次从左上角裁切读取失败，尝试冲底部裁切和最后一帧的中部裁切读取 '''
    ''' 坐标: img1 = 240:1234:255:35   img2 = 280:336:334:80 '''

    final_result = ''

    img1_crop = frameimg1 + '_2st_crop.jpeg'
    img2_crop = frameimg2 + '_2st_crop.jpeg'

    crop_start_cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -filter:v "crop=255:35:240:1235" %s' % (frameimg1, img1_crop)
    crop_end_cmd   = 'ffmpeg -hide_banner -v quiet -stats -i %s -filter:v "crop=334:80:280:336" %s' % (frameimg2, img2_crop)
    os.system(crop_start_cmd)
    os.system(crop_end_cmd)

    first_result  =   DetectTextFromImage(img1_crop)
    second_result =   DetectTextFromImage(img2_crop)
    
    os.unlink(frameimg1)
    os.unlink(frameimg2)
    os.unlink(img1_crop)
    os.unlink(img2_crop)

    for first in first_result:
        first_tup =  first
        for tup_ele in first_tup:
            if isinstance(tup_ele, str):
                final_result = final_result + tup_ele + '\\'

    for second in second_result:
        second_tup = second 
        for tup_ele in second_tup:
            if isinstance(tup_ele, str):
                final_result = final_result + tup_ele + '\\'

    if final_result != '':
        return final_result
    else:
        return None

    


def ClassVideo(path):
    ''' remove m3u8  file first. find . -size -10k '''
    file_type =''
    
    readId = []

    idfile = './id'
    if os.path.exists(idfile):
        fd = open(idfile, 'a+', encoding='utf-8')
    else:
        fd = open(idfile, 'w+', encoding='utf-8')
    lst = os.listdir(path)
    for f in lst:
        final_result = ''
        file_path = path + f
        if os.path.isfile(file_path) and IsVideoFile(file_path):
            duration = float(GetMediaInfo(file_path,'duration'))
            if duration < float(500):
                img1 = file_path + '_img01.jpeg'
                img2 = file_path + '_img02.jpeg'
                if os.path.exists(img1):
                    os.unlink(img1)
                if os.path.exists(img2):
                    os.unlink(img2)

                cmd1 = 'ffmpeg -hide_banner -v quiet -stats -ss 00:00:00 -to 00:00:01  -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(file_path, img1)

                start = round((duration - 1), 2)
                end   = round(duration, 2)
                cmd2 = 'ffmpeg -hide_banner -v quiet -stats -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(start, end, file_path, img2)
                os.system(cmd1)
                os.system(cmd2)
                
                img1_crop = img1 + '_crop.jpeg'
                img2_crop = img2 + '_crop.jpeg'
                if os.path.exists(img1_crop):
                    os.unlink(img1_crop)
                if os.path.exists(img2_crop):
                    os.unlink(img2_crop)

                ''' 宽:高:起始X:起始Y'''
                crop_start_cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -filter:v "crop=236:53:13:71" %s' % (img1, img1_crop)
                crop_end_cmd   = 'ffmpeg -hide_banner -v quiet -stats -i %s -filter:v "crop=360:55:186:314" %s' % (img2, img2_crop)
                os.system(crop_start_cmd)
                os.system(crop_end_cmd)
                first_result  =   DetectTextFromImage(img1_crop)
                second_result =   DetectTextFromImage(img2_crop)

                for first in first_result:
                    first_tup =  first
                    for tup_ele in first_tup:
                        if isinstance(tup_ele, str):
                            final_result = final_result + tup_ele + '\\'

                for second in second_result:
                    second_tup = second 
                    for tup_ele in second_tup:
                        if isinstance(tup_ele, str):
                            final_result = final_result + tup_ele + '\\'
                print('=====================================================================')
                print('%ss--%s' % (file_path, duration))
                print(final_result)
                print('=====================================================================')

                if final_result == '':
                    os.unlink(img1_crop)
                    os.unlink(img2_crop)
                    final_result = ReadTextFromMiddleCrop(img1, img2)
                    print('******************************Second Crop:  %s ' % file_path)
                    print(final_result)
                    print('*******************************************************************************')
                else:
                    os.unlink(img1)
                    os.unlink(img2)
                    os.unlink(img1_crop)
                    os.unlink(img2_crop)

                infs = '%s--%s\n' % (file_path, final_result )
                fd.write(infs)

                ##MoveRecordToDir(path, dst_path)
                ## Mid crop
               
            else:
                ##MoveProductToDir(path, dst_path)
                print('%ss--%s' % (file_path, duration))
    fd.close()


ClassVideo(SrcDir)

''' ffmpeg  -i  ./0001.jpeg  -filter:v "crop=236:53:13:71"  out.jpeg '''
##ffmpeg -ss   -i  ./00315.mp4  -f image2 -vf   fps=fps=1/1 -qscale:v 2 ./mp4-%05d.jpeg



