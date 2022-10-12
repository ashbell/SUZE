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

def   GetMediaInfo(path='', attr=''):
    info = {'codec':'', 'size':'','duration':0.00}
    if os.path.exists(path):
        cmd = 'ffprobe -v quiet -show_streams -print_format json %s' % path
        output = subprocess.getoutput(cmd)
        ''' Fuck this output'''
        output = output.replace('Active code page: 65001', '')
    try:     
        json_data       = json.loads(output)
        info['codec']   = json_data['streams'][0]['codec_name']
        width           = json_data['streams'][0]['width']
        height          = json_data['streams'][0]['height']
        info['size']    = '%sx%s' % (width,height)
        info['duration']= json_data['streams'][0]['duration']
    except:
        print('Get Media info Failed: %s' % path)
        return 'unknow'
        ##exit() 
    if attr != '':
        return info[attr]
    else:
        return info

def   DetectTextFromImage(path):
    ''' 获取单个图片的文本，并返回结果'''
    result = ''
    reader = easyocr.Reader(['ch_sim','en'], gpu=False,verbose=False)
    with open(path, 'rb') as f:
        img = f.read()
        result = reader.readtext(img)

        for res in result:
            pass
        ##print ('%s--%s' %(result[0][1], result[0][2]))
    return result



def   GetPicOfSecond(mp4='', sec=''):
    ''' 对视频每一秒截屏一次，默认时间为1秒，0001.mp4_00123.png'''
    if sec == '':
        sec = 1

    file_names = []
    if os.path.isfile(mp4) and os.path.exists(mp4):
        duration =  GetMediaInfo(mp4, 'duration') 
        try:
            duration = float(duration)
        except:
            print('Get Duration of: %s Failed' % mp4)

        count = round(duration/int(sec)) + 1
        for num in range(1, count):
            file_name = '%s_%05d.png' % (mp4, num)
            file_names.append(file_name)
            ##print(file_name)

        out = '%s_' % (mp4)
        out = out + '%05d.png'
        cmd = 'ffmpeg -nostats -loglevel 0  -y -i %s -f image2 -vf fps=fps=1/%d  %s' \
            % (mp4, int(sec), out)
        print(cmd)
        os.system(cmd)
    
    return file_names

"""
    高度 15个像素， 距离左边 20像素，顶部65像素，宽度175像素：  左上
    高度 15个像素， 距离右边 20像素，底部20像素，宽度175像素：  右下
    高度 15个像素， 距离左边175像素,  顶部250个像素，宽度 250像素 中部
    高度 15个像素， 距离左边175像素,  底部10个像素，宽度 250像素 老中部开头
    高度 40 个像素，距离左边210个，   距离顶部260个像素，宽度175  老中部
    对于直接保存没有合成的视频，采用抽首尾两张的方法，截取5个区域的图片来识别
    对于合成的，视频长度超过50秒的，每隔10秒抽一张，截取5个区域来识别
"""
def   CropImageTextArea(image='', sizex='', sizey=''):
    pic_list = []
    x = int(sizex)
    y = int(sizey)
    LeftTop     = [ 300, 120, 0,  0 ]
    RightBottom = [ 300, 120, x-300,  y ]
    LogoMid     = [ x, 250, 0, 50]
    OldStartMid      = [ 300, 120, (x-300)/2, y-120]
    OldEndMid    = [ x, 250, 0, 50 ]
    img_lt = image + '_lt.png'
    img_rb = image + '_rb.png'
    img_lgmid = image + '_logo_mid.png'
    img_oldstartmid = image +'_old_midstart.png'
    img_oldendmid = image + '_old_endmid.png'
    cmd_lt = 'ffmpeg -nostats -loglevel 0  -y -i %s -filter:v "crop=%d:%d:%d:%d" %s' % \
               (image, LeftTop[0], LeftTop[1], LeftTop[2], LeftTop[3], img_lt)
    cmd_rb = 'ffmpeg -nostats -loglevel 0  -y -i %s -filter:v "crop=%d:%d:%d:%d" %s' % \
               (image, RightBottom[0], RightBottom[1], RightBottom[2] , RightBottom[3], img_rb)

    cmd_lgmid = 'ffmpeg -nostats -loglevel 0  -y -i %s -filter:v "crop=%d:%d:%d:%d" %s' % \
               (image, LogoMid[0], LogoMid[1], LogoMid[2], LogoMid[3], img_lgmid)

    cmd_old = 'ffmpeg -nostats -loglevel 0  -y -i %s -filter:v "crop=%d:%d:%d:%d" %s' % \
               (image, OldStartMid[0], OldStartMid[1], OldStartMid[2], OldStartMid[3], img_oldstartmid)

    cmd_oldendmid = 'ffmpeg -nostats -loglevel 0  -y -i %s -filter:v "crop=%d:%d:%d:%d" %s' % \
               (image, OldEndMid[0], OldEndMid[1], OldEndMid[2], OldEndMid[3], img_oldendmid)
    print('Do - CropImageTextArea:')
    
    os.system(cmd_lt)
    os.system(cmd_rb)
    os.system(cmd_lgmid)
    os.system(cmd_old)
    os.system(cmd_oldendmid)
    pic_list.append(img_lt)
    pic_list.append(img_rb)
    pic_list.append(img_lgmid)
    pic_list.append(img_oldstartmid)
    pic_list.append(img_oldendmid)

    return pic_list
    


def  GetPicOfStartAndEnd(mp4=''):
    ''' 获取视频的开始和最后一张图片,然后对两张图片做10次裁剪，分别得出文本'''
    result_lst = []
    if os.path.isfile(mp4):
        info        = GetMediaInfo(mp4, '')
        sizex       = info['size'].split('x')[0]
        sizey       = info['size'].split('x')[1]
        duration    = float(info['duration'])
        
        startImage = mp4 + '_start.png' 
        endImage   = mp4 + '_end.png'

        start = 1
        end   = start + 1

        startCmd = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(start, end, mp4, startImage)
        start = duration - 1
        end   = duration
        endCmd = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(start, end, mp4, endImage)
        print('Do - GetPicOfStartAndEnd:')
        os.system(startCmd)
        os.system(endCmd)

        result_lst = CropImageTextArea(startImage, sizex, sizey)
        result_lst = result_lst + CropImageTextArea(endImage, sizex, sizey)
        print('Do - Delete Start && End Image.')
        os.unlink(startImage)
        os.unlink(endImage)
    return result_lst



def   GetTextOfPics(pic_list=[]):
    ''' 从MP4生成的图片序列中中获取每个图片中的文本，并处理得到的文本组合'''
    print('Do - GetTextOfPics: pic_list=[]')
    texts = []
    for pic in pic_list:
        result = DetectTextFromImage(pic)
        for res in result:
            texts.append(res[1])

    print('Do - Delete: pic_list=[]')
    for img in pic_list:
        os.unlink(img)
    return texts


''' d=''; for s in {A..Z}; do d=$d"'"$s"'",; done; echo $d  '''
legal_table = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', \
               'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
               '0','1','2','3','4','5','6','7','8','9',\
               '_','-']

def   FormatTextResult(string=''):
    ''' 格式化处理文本，删除不可作为ID账号的文本字符, 数字，字母，下划线，减号'''
    result = [] 
    lst = list(string)
    for c in lst:
        if c in legal_table:
            result.append(c)
    return ''.join(result)


def   ProcessResultTexts(texts=[]):
    ''' 取得这个MP4对应下所有可能的结果'''
    result = []
    for text in texts:
        if len(text) > 7:
            result.append( FormatTextResult(text) )
    return result

def   FindMaxCountChar(string=''):
    ''' 找个找个字符串中，出现次数最多的字符 '''
    s_lst = list(string)
    count = []
    max_count = 0
    max_char = ''
    for c in s_lst:
        if c in legal_table:
            count.append(s_lst.count(c))
    
    max_count = max(count)
    for c in s_lst:
        if s_lst.count(c) == max_count:
            max_char = c
            break
    return max_char
    

def   GuessUserIDFromTextList(id_lst = []):
    ''' 从所有得到的文本中，猜测出哪个是最有可能是ID'''
    print('Do - GuessUserIDFromTextList.')
    len_list = []
    for x in id_lst:
        len_list.append(len(x))
    if len(len_list) > 0:
        max_len = max(len_list)
        min_len = min(len_list)
    else:
        print('-------- GuessUserIDFromTextList Error, empty len_list')
        exit(0)

    '''  左边补齐到最大长度'''
    left_align  =  []
    right_align =  []
    table_len   =  len(id_lst)
    for num in range(0, table_len):
        lenx = len(id_lst[num])
        left = list(id_lst[num])
        right = []
        if lenx != max_len:
            diff = max_len - lenx
            diff_next = diff +  1
            
            ''' 左边对齐，补右边'''
            for d in range(1, diff_next):
                left.append('*')
            left_align.append( ''.join(left) )

            ''' 右边对齐, 补左边 '''
            for d in range(0, diff):
                right.append('*')
            right = right + list(id_lst[num]) 
            right_align.append(''.join(right))
        else:
            left_align.append(id_lst[num])
            right_align.append(id_lst[num])
            
    left_col    = []
    col_count   = len(left_align)
    tmp         = []
    num         = row = 0

    while (row < col_count) and (num < max_len):
        x_lst = list(left_align[row])
        tmp.append(x_lst[num])
        if len(tmp) < col_count:
            row = row + 1
        else:
            left_col.append(''.join(tmp))
            num = num + 1
            tmp = []
            row = 0

    user_id = []
    for x in left_col:
        max_char = FindMaxCountChar(x)
        user_id.append(max_char)
    most = ''.join(user_id)
    return most
    '''  右边对齐到最大长度，前面补空格'''

def  MoveToDir(mp4_file='', hastext=''):
    print('Do - MoveToDir. Para: file = %s -- hastext = %s ' %(mp4_file, hastext))
    mp4_dir = '\\'.join(mp4_file.split('\\')[0:-1]) + '\\'
    mp4_name = mp4_file.split('\\')[-1]
    DirHasText = mp4_dir + hastext+ '\\'
    info = ''
    if os.path.exists(DirHasText):
        pass
    else:
        os.makedirs(DirHasText)
    new_mp4_path = DirHasText + mp4_name
    if os.path.exists(new_mp4_path):
        print('Move - Src: %s to Dst: %s exists, skip' % (mp4_file, new_mp4_path) )
        info = '%s \t-> %s  exists.\n' % (mp4_file, new_mp4_path) 
    else:
        print('Move - Src: %s to Dst: %s .' % (mp4_file, new_mp4_path) )
        info = '%s \t-> %s .\n' % (mp4_file, new_mp4_path) 
        shutil.move(mp4_file, new_mp4_path)
    print('Move - Done.')
    return info



def  ClassHasTextMp4ToDir(mp4_file):
    ''' 根据所给的MP4, 查找是否含有ID，有则移动到has目录，写入log，没有移动到nohas目录，写入log'''
    img_lst = GetPicOfStartAndEnd(mp4_file)
    texts = GetTextOfPics(img_lst)
    LogInfo = ''
    for txt in texts:
        print('Get - \t%s' % txt)
    id_lst = ProcessResultTexts(texts)

    proc_file = './proc_file'
    if os.path.exists(proc_file):
        fproc = open(proc_file, 'a+', encoding='utf-8')
    else:
        fproc = open(proc_file, 'w+', encoding='utf-8')

    fproc.write(mp4_file + '\n')
    for val in id_lst:
        s = '--%s\n' % val
        fproc.write(s)
    proc_file.close()

    if len(id_lst) > 0:
        user_id = GuessUserIDFromTextList(id_lst)
        info = MoveToDir(mp4_file, 'has')
        
        print('Get - %s\tResult:  %s' % (mp4_file, user_id))
    else:
        user_id = 'None'
        info = MoveToDir(mp4_file, 'nohas')
        print('Get - %s\tResult:  None' % mp4_file )

    LogInfo = '%s--%s\n' % (info, user_id)
    return LogInfo


def IsVideoFile(path):
    ftype = mimetypes.guess_type(path)
    if 'mp4' in ftype[0]:
        return True
    else:
        return False


def  FindText(path=''):
    ''' 对指定目录下的所有MP4扫描, 以'\\'结尾'''
    mp4_list = []
    info = ''
    if os.path.isdir(path):
        file_list = os.listdir(path)
        for f in file_list:
            mp4_file = path + f
            if os.path.isfile(mp4_file) and IsVideoFile(mp4_file):
                mp4_list.append(mp4_file)
    log = './logfile'
    if os.path.exists(log):
        fw = open(log, 'a+', encoding='utf-8')
    else:
        fw = open(log, 'w+', encoding='utf-8')

    for mp4_file in mp4_list:
        print('Do - Scan: %s' % mp4_file)
        info = ClassHasTextMp4ToDir(mp4_file)
        fw.write(info)
    fw.close()


FindText(SrcDir)

"""
''' 参数必须是 mp4文件的根目录'''
def   ClassSizeToDir(path):
    if path[-1] != '\\':
        path = path + '\\'
    lst = os.listdir(path)
    if os.path.exists('./mv_log'):
        fw = open('./mv_log', 'a+', encoding='utf-8')
    else:
        fw = open('./mv_log', 'w+', encoding='utf-8')

    for f in lst:
        mp4_file = path + f
        if os.path.isfile(mp4_file):
            size = GetMediaInfo(mp4_file, 'size')
            size_dir = path + size + '\\'
            if (os.path.isdir(size_dir)) and ( os.path.exists(size_dir)):
                pass
            else:
                os.makedirs(size_dir)
            new_path = size_dir + f 
            print('%s---%s'%(mp4_file, new_path))    
            if (not os.path.exists(new_path)) and (os.path.isfile(mp4_file)):
                fw.write('%s -- %s\n' %(mp4_file, new_path))
                shutil.move(mp4_file, new_path)
            else:
                print('%s   -  dst file: %s  exists' % (mp4_file, new_path))
                fw.write('%s -- %s  -- dst exists!\n' %(mp4_file, new_path))
        else:
            pass
            ##print('%s is not a mp4 file' % mp4_file)
    fw.close()
                
ClassSizeToDir(SrcDir)






def DetectTextFromImage(path):
    reader = easyocr.Reader(['ch_sim','en'], gpu=False, verbose=False)
    with open(path, 'rb') as f:
        img = f.read()
        result = reader.readtext(img)

        for res in result:
            pass
            print ('%s--%s' %(result[0][1], result[0][2]))
        return result

''' 根据分辨率，查找包含有ID账号的视频, './final/size[720x1280]'''
def   FindMp4ContainText(size=''):
    mp4_dir = SrcDir + size + '\\'
    if os.path.isdir(mp4_dir) and os.path.exists(mp4_dir):
        lst = os.listdir(mp4_dir)
    else:
        print('Invalid dir: %s' % mp4_dir)
        exit()

    for f in lst:
        final_result = ''
        mp4_file = mp4_dir + f
        if os.path.isfile(mp4_file) and IsVideoFile(mp4_file):
            duration = float(GetMediaInfo(mp4_file,'duration'))
            img1 = mp4_file + '_img01.jpeg'
            img2 = mp4_file + '_img02.jpeg'


            if os.path.exists(img1):
                os.unlink(img1)
            if os.path.exists(img2):
                os.unlink(img2)
            ##cmd1 = 'ffmpeg -hide_banner -v quiet -stats -ss 00:00:00 -to 00:00:01  -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
            cmd1 = 'ffmpeg -nostats -loglevel 0  -ss 00:00:00 -to 00:00:01  -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(mp4_file, img1)

            start = round((duration - 1), 2)
            end   = round(duration, 2)
            ##cmd2 = 'ffmpeg -hide_banner -v quiet -stats -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
            cmd2 = 'ffmpeg -nostats -loglevel 0  -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                    %(start, end, mp4_file, img2)

            os.system(cmd1)
            os.system(cmd2)
            img1_crop = img1 + '_crop.jpeg'
            img2_crop = img2 + '_crop.jpeg'


            if os.path.exists(img1_crop):
                os.unlink(img1_crop)
            if os.path.exists(img2_crop):
                os.unlink(img2_crop)
            
            crop_start_cmd = 'ffmpeg -nostats -loglevel 0  -i %s -filter:v "crop=236:53:13:71" %s' % (img1, img1_crop)
            crop_end_cmd   = 'ffmpeg -nostats -loglevel 0  -i %s -filter:v "crop=360:55:186:314" %s' % (img2, img2_crop)
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
            print('%ss--%s' % (mp4_file, duration))
            print(final_result)
            print('=====================================================================')

            if final_result == '':
                os.unlink(img1_crop)
                os.unlink(img2_crop)
                ##final_result = ReadTextFromMiddleCrop(img1, img2)
                print('********First detect Null:  %s ' % mp4_file)
                print(final_result)
                print('*******************************************************************************')
            else:
                os.unlink(img1)
                os.unlink(img2)
                os.unlink(img1_crop)
                os.unlink(img2_crop)

                infs = '%s--%s\n' % (mp4_file, final_result )
                fw.write(infs)

    fw.close()
             
        
FindMp4ContainText('720x1280')




fd = open('./id', 'r', encoding='utf-8')
lines = fd.readlines()
fd.close()

for line in lines:
    line = line.strip('\n')
    ##print(line)
    result = re.findall("\'.*?\'", line)
    print(result)

    for res in result:
        print(re.findall('\w.*', res))
"""
