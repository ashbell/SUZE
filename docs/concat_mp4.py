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

Mp4Dirs = []
OmitDirFlag = ['del.txt', 'ok', 'proc.txt']
NeedCombine = []

def GetMp4FileDir(SrcDir):
    DirLists = os.listdir(SrcDir)
    for SubDir in DirLists:
        Path = SrcDir + SubDir

        if os.path.isdir(Path):
            Path = Path + '\\'
            """
            PathEnd = Path[-5:]
            if '\\mp4\\' == PathEnd:
                Mp4Dirs.append(Path)
            """
            GetMp4FileDir(Path)
        elif 'dd.txt' in Path:
            NeedCombine.append(Path)
        else:
            pass


Mp4List = []
def GetAllMp4Files(Mp4Dir):
    FileLists = os.listdir(Mp4Dir)
    for File in FileLists:
        Path = Mp4Dir + File
        if os.path.isdir(Path):
            Path = Path + '\\'
            GetAllMp4Files(Path)
        elif (os.path.isfile(Path)) and ('.mp4' in Path):
            Mp4List.append(Path)
        else:
            pass

def IsDirEmpty(path):
    LenFileList = len(os.listdir(path))
    if LenFileList > 0:
        return True
    else:
        return False
             
def ReszieMp4(FilePath, x, y):

    OutX = 720
    OutY = 1280
    cropx = 0
    cropy = 0
    cmd=''
    recursion = 0

    ''' x,y为固有的分辨率'''
    print('\tResize %s : %d x  %d' % (FilePath,x,y))
    OutDir = '\\'.join(FilePath.split('\\')[0:-1]) + '\\'
    FileName = FilePath.split('\\')[-1].split('.')[0] + '_'+str(random.randint(100,999)) + '.mp4'
    OutFile = OutDir + FileName
    
    '''视频裁剪处理部分'''
    if (x < OutX) and (y < OutY):
        scalex = round(float(OutX)/x, 3)
        scaley = round(float(OutY)/y,3)
        if scalex == scaley:
            ''' 等比缩放 '''
            scalex_to  = round(scalex * x)
            scaley_to  = round(scaley * y)
            cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                  %(FilePath, scalex_to, scaley_to,OutFile)
            print('\n>1:EqualScale: %s\n' % cmd)
            os.system(cmd)
        else:
            ''' 不是等比，需要缩放后裁剪  480 x 640 -> 1.5 = 720x960 '''
            yto = round(float(OutY)/y, 3)
            xto = round(float(OutX)/x, 3)
            tmp = OutFile + '_tmp.mp4'
            if xto > yto:
                scalecmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=720:-2 -preset slow  -crf 20 %s 2>&1 ' \
                    %(FilePath,  tmp)
                print('\n>1-1:ScaleLarge: %s\n' % scalecmd)
                os.system(scalecmd)
            if xto < yto:
                scalecmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=-2:1280 -preset slow  -crf 20 %s 2>&1 ' \
                    %(FilePath,  tmp)
                print('\n>1-2:ScaleLarge: %s\n' % scalecmd)
                os.system(scalecmd)

            ''' 对视频进行裁剪，'''
            tmpclip = VideoFileClip(tmp)
            tmpX = tmpclip.size[0]
            tmpY = tmpclip.size[1]
            tmpclip.reader.close()
            tmpclip.audio.reader.close_proc()
            ''' 原来的处理：480x640 缩放之后是 720 960， 还是不能裁剪，直接就原图放进去了'''
            ''' X缩放倍数大于Y的，所以Y必然大于1280'''
            if tmpX == '720':
                cropy = round( (tmpY - OutY)/2 )
                cropx = 0
            ''' Y缩放倍数大于X，所以X必然大于720'''
            if tmpY ==1280:
                cropy = 0
                cropx = round( (tmpX - OutX)/2)

            cropcmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                %( tmp, OutX, OutY, cropx,  cropy, OutFile)

            if os.path.exists(tmp):
                print('>1-2:Crop: %s\n'% cropcmd)
                os.system(cropcmd)
                os.unlink(tmp)
            else:
                print('\n>1-2:Crop: ....NOT FOUND FILE: %s' % tmp)


    ''' X 需要缩放，Y需要裁切'''
    if ( x < OutX) and (y >= OutY):
        scalex = round(float(OutX)/x, 3)
        scalex_to = round(scalex * x)
        if scalex_to % 2 !=0:
            if scalex_to > OutX:
                scalex_to = scalex_to - 1
            else:
                scalex_to = scalex_to + 1
        ''' 先把它放大'''
        tmp = OutFile + '_tmp.mp4'
        cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=%d:-2 -preset slow  -crf 20 %s 2>&1 ' \
                  %(FilePath, scalex_to, tmp)
        print('\n>2-1:ScaleLarge: %s\n' % cmd)
        os.system(cmd)

        tmpclip = VideoFileClip(tmp)
        tmpY = tmpclip.size[1]
        tmpclip.reader.close()
        tmpclip.audio.reader.close_proc()
        
        cropx = 0
        cropy = round( (tmpY - OutY)/2 )
        cropcmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                %( tmp, OutX, OutY, cropx,  cropy, OutFile )

        if os.path.exists(tmp):
            print('>2-2:Crop: %s\n'% cropcmd)
            os.system(cropcmd)
            os.unlink(tmp)
        else:
            print('\n>2-2:Crop: ....NOT FOUND FILE: %s' % tmp)
    
    ''' 给的高比规定的要大的时候，切掉多余的高 '''
    if ( x >= OutX ) and (y >= OutY):
        scalex = round(float(x)/OutX, 3)
        scaley = round(float(y)/OutY, 3)

        if scalex == scaley:
            scalex = round(float(1)/scalex, 3)
            scacmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=iw*%f:-2 -preset slow  -crf 20 %s 2>&1 ' \
                  %(FilePath, scalex, OutFile)
            print('\n>3-1:EqualReduce: %s\n' % scacmd)
            os.system(scacmd)
        else:
            tmp = OutFile + '_tmp.mp4'
            scacmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=iw*%d:-2 -preset slow  -crf 20 %s 2>&1 ' \
                  %(FilePath, scalex, tmp)
            print('\n>3-2-1:Reduce: %s\n' % scacmd)
            os.system(scacmd)

            if os.path.exists(tmp):
                tmpclip = VideoFileClip(tmp)
                tmpY = tmpclip.size[1]
                tmpclip.reader.close()
                tmpclip.audio.reader.close_proc()
            
                cropx = 0
                gap = tmpY - OutY
                if gap > 0:
                    cropy = round(gap/2)
                else:
                    cropy = 0

                cropcmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                    %( tmp, OutX, OutY, cropx,  cropy, OutFile)
                if os.path.exists(tmp):
                    print('\n>3-2-2:Crop: %s\n' % cropcmd)
                    os.system(cropcmd)
                    os.unlink(tmp)
                else:
                    print('\n>3-2-2:Crop: NOT FOUND: %s' % tmp)

    ''' 恒屏的裁切, 直接旋转得了，不截了ffmpeg -i a.mp4 -vf "vflip" /b.mp4. vflip 即表示垂直翻转.  '''
    ''' transpose=0，表示：逆时针旋转90度并垂直翻转  '''
    ''' transpose=1，表示：顺时针旋转90度  '''
    ''' transpose=2，表示：逆时针旋转90度  '''
    ''' transpose=3，表示：顺时针旋转90度后并垂直翻转. '''
    if ( x >= OutX ) and (y < OutY) and ( x > y):
        tmp = OutFile + '_tmp.mp4'
        
        rotatecmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf transpose=1 -preset slow  -crf 20 %s 2>&1 ' \
                    %( FilePath, tmp)
        ##rotatecmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf transpose=1  %s 2>&1 ' \
        ##            %( FilePath, tmp)
        print('\n>4-1:Rotate: %s\n' % rotatecmd)
        os.system(rotatecmd)
        clip = VideoFileClip(tmp)
        tmpX = clip.size[0]
        tmpY = clip.size[1]
        clip.reader.close()
        clip.audio.reader.close_proc()
        if os.path.exists(tmp):
            recursion = 1
            print('\n>4-2: CallBack: %s :[ %d * %d ]\n' % (tmp, tmpX, tmpY))
            ReturnTmp = ReszieMp4(tmp, tmpX, tmpY)
            OutFile = ReturnTmp
            recursion = 0
        ##return ReturnTmp

    """ 720 x 960 的视频 会造成死循环,旋转得到 960x720，又是横屏，又旋转
        补充处理这种视频，直接放大，裁剪        
    """
    if ( x >= OutX ) and (y < OutY) and( x < y ):
        tmp = OutFile + '_tmp.mp4'
        scalecmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=-2:1280 -preset slow  -crf 20 %s 2>&1 ' \
                  %(FilePath, tmp)
        print('[ 5-1:Scale ]: %s\n'% scalecmd)
        os.system(scalecmd)

        clip = VideoFileClip(tmp)
        tmpX = clip.size[0]
        clip.reader.close()
        clip.audio.reader.close_proc()
        cropx = round((tmpX - OutX)/2)
        cropy = 0
        cropcmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                %( tmp, OutX, OutY, cropx,  cropy, OutFile)


        if os.path.exists(tmp):
            print('[ 5-2:Crop ]: %s\n'% cropcmd)
            os.system(cropcmd)
            os.unlink(tmp)
        else:
            print('\n[ 5-2:Crop ]: NOT FOUND: %s' % tmp)
            exit()
        



    if recursion == 1:
        print('\t Rescurion, none return')
    else:
        '''处理完的视频，将原有的挪走到指定位置，备用'''
        BadDir = FilePath.split('\\mp4\\')[0] + '\\' + 'bad_orgmp4\\'
        BadName = FilePath.split('\\mp4\\')[1].replace('\\','_')
        if not os.path.exists(BadDir):
            os.makedirs(BadDir)
        NewBadPath = BadDir + BadName
        shutil.move(FilePath, NewBadPath)
        ##print('return END: main: %s'% OutFile)
        return OutFile



def GetMediaInfo(path):
    if os.path.exists(path):
        cmd = 'ffprobe -v quiet -show_streams -print_format json %s' % path
        output = subprocess.getoutput(cmd)
        ''' Fuck this output'''
        output = output.replace('Active code page: 65001', '')
        json_data = json.loads(output)
    if not 'streams' in json_data:
        print('Get Media info Failed')
        exit()
    else:
        return (json_data['streams'][0]['codec_name'])


    
def MergeToFile(OutFile = '', lst = []):
    lst.sort()
    tslst = []
    InputFile = OutFile + '_lst.txt'
    fw = open(InputFile, 'w+', encoding='utf-8')
    for l in lst:
        tsfile = l + '_.mts'
        tslst.append(tsfile)
        info = 'file  \'%s\'\n' % tsfile 
        ##info = 'file  \'%s\'\n' % l 
        codec_name = GetMediaInfo(l)
        print('Convert -  %s \t %s '  % (codec_name, l))
        ''' ffmpeg -i abc.mp4 -c:v libx264 -c:a aac -b:a 160k -bsf:v h264_mp4toannexb -f mpegts -crf 32 pqr.ts'''
        """
            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s   -vcodec copy -acodec copy -vbsf h264_mp4toannexb -q 0 %s' \
            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s   -vcodec copy -acodec copy -vbsf hevc_mp4toannexb -q 0 %s' \

            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s  -c:v libx264 -c:a aac -b:a 160k -bsf:v  h264_mp4toannexb -f mpegts -crf 32 %s' \
            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s  -c:v libx265 -c:a aac -b:a 160k -bsf:v  hevc_mp4toannexb -f mpegts -crf 32 %s' \
        """

        if 'h264' in codec_name :
            ##totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s -g 1 -keyint_min 1  -c: copy -bsf:v  h264_mp4toannexb -f mpegts %s' \
            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s -q 0   %s' \
                        % (l, tsfile)
        elif 'hevc' in codec_name:
            totscmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s -q 0   %s' \
                % (l, tsfile)
        else:
            print('***Unkonwn Codec: %s ******************' % l)
            exit()
        os.system(totscmd)
        fw.write(info)
    fw.close()

    """
    ffmpeg -i 0.mp4 -c:v h264_nvenc -preset fast -rc vbr -qmin 1 -qmax 1 -filter_complex "[0:v]trim=start=01.00:duration=03.00,setpts=PTS-STARTPTS[vmiddle]" -video_track_timescale 18000 -map [vmiddle] middle_0.mp4
    Those numbers in the ffprobe readout are presentation timestamps and inform the player when to display each frame. They are denominated in terms of a timebase. So, a PTS of 600 with a timebase of 1/1200 (or timescale of 1200), means a display time of 600 * 1/1200 = 0.5 seconds, as does a PTS of 700 with a timescale of 1400. Now, when two videos with different timebases are joined, the result won't be correct since ffmpeg will adopt the timebase of the first video as the definitive value. I added a parameter to make those uniform.

    """

    ##OutFile = OutFile +'.ts'
    ##cmd = 'ffmpeg -hide_banner -v quiet -stats -f concat -safe 0 -i %s -q 0 -c copy %s' \
    ##cmd = 'ffmpeg -hide_banner  -f concat -safe 0 -i %s -ac 1 -ar 48000 -vcodec copy -g 1 -keyint_min 1 -q 0  %s' \
    cmd = 'ffmpeg -hide_banner  -f concat -safe 0 -i %s -c copy  %s' \
            % (InputFile, OutFile)
    print('\n>Merge: %s\n' % cmd)
    os.system(cmd)

    """ Get origin MPEG-4 FILE Large  need to user H264/H265 codec to MP4"""
    
    for ts in tslst:
        if os.path.exists(ts):
            os.unlink(ts)

    return 0


GetMp4FileDir(SrcDir)
for combine in NeedCombine:
    lst = []
    Mp4List = []
    ClipList = []
    Mp4SizeOK = 1
    LogFile    = '\\'.join(combine.split('\\')[0:-1]) + '\\' + 'Log.log'
    NeedDoFlagFile    = '\\'.join(combine.split('\\')[0:-1]) + '\\' + 'dd.txt'
    if os.path.isfile(LogFile):
        Fd_Log = open(LogFile, 'a+', encoding='utf-8')
    else:
        Fd_Log = open(LogFile, 'w+', encoding='utf-8')

    CombineDir = '\\'.join(combine.split('\\')[0:-1]) + '\\' + 'mp4\\'
    TimeNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if os.path.exists(CombineDir) and IsDirEmpty(CombineDir):
        print('------------------%s--------------------'% CombineDir)
        Fd_Log.write('------%s--------%s--------------\n'% (TimeNow, CombineDir))
        GetAllMp4Files(CombineDir)
        for Mp4File in Mp4List:
            VideoClip = VideoFileClip(Mp4File)
            ClipList.append(VideoClip)
            VideoSizeX = VideoClip.size[0]
            VideoSizeY = VideoClip.size[1]
            print('\tProces %s' % Mp4File)
            if (VideoSizeX == 720) and ( VideoSizeY == 1280):
                lst.append(Mp4File)
            else:
                ''' 转换之后要移动到别出去，所以先关闭文件的读写句柄'''
                VideoClip.reader.close()
                VideoClip.audio.reader.close_proc()
                Mp4SizeOK = 0
                NewResizeFile = ReszieMp4(Mp4File, VideoSizeX, VideoSizeY)
                ##VideoClip = VideoFileClip(NewResizeFile)
                lst.append(NewResizeFile)
                ##ClipList.append(VideoClip)

                print('\tVideo Size :%s  [ %d X %d ] is not OK.....' % (Mp4File, VideoSizeX, VideoSizeY))
                Fd_Log.write('\tVideo Size :%s:   [ %d X %d ] is not OK.....\n' % (Mp4File, VideoSizeX, VideoSizeY))
                Fd_Log.write('\tConvert :%s:   [ %d X %d ] to %s.....\n' % (Mp4File, VideoSizeX, VideoSizeY, NewResizeFile))

            Fd_Log.write('\t%s\n' % Mp4File)
            VideoClip.reader.close()
            VideoClip.audio.reader.close_proc()

    if len(ClipList) > 0:
        ##OutClip = concatenate_videoclips(ClipList, method='compose')
        RandomStr = str(random.randint(100,999)) + str(random.randint(10,99)) + '.mp4'
        OutFile = '\\'.join(combine.split('\\')[0:-1]) + '\\'+ 'concat_' + RandomStr 
        print('\tWrite  : %s' % OutFile)
        ##OutClip.to_videofile(OutFile)
        '''   My func'''
        ##MergeToFile(OutFile, lst)
        TimeNow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Fd_Log.write('\\ %s \\ Write  : %s   end..\n\n' % (TimeNow,OutFile))
        if os.path.exists(NeedDoFlagFile):
            os.unlink(NeedDoFlagFile)
    Fd_Log.close()

"""
for Mp4Dir in Mp4Dirs:
    ##print('Woring @: %s' % Mp4Dir)
    GetAllMp4Files(Mp4Dir)        
"""

"""
def GetAllMp4SubDirs():
    DirInfo = {}
    GetMp4FileDir(SrcDir)
    for Mp4Dir in Mp4Dirs:
        Dirlists = os.listdir(Mp4Dir)
        for SubDir in Dirlists:
            ClassDir = Mp4Dir + SubDir
            if os.path.isdir(ClassDir):
                if not(Mp4Dir in DirInfo.keys()):
                    DirInfo[Mp4Dir] = [ClassDir]
                else:
                    DirInfo[Mp4Dir].append(ClassDir)
    return DirInfo

def GetAllMp4Files():
    Mp4Info = {}
    DirInfo = GetAllMp4SubDirs()
    for Dir in DirInfo.keys():
        print(Dir)
        print('----------------------')
        ClassPathes = DirInfo[Dir]
        for ClassPath in ClassPathes:
            if os.path.isdir(ClassPath):
                Mp4Files = os.listdir(ClassPath)
                for Mp4File in Mp4Files:
                    Mp4Path = ClassPath + '\\' + Mp4File
                    if os.path.exists(Mp4Path):

        print('====================================')
"""


