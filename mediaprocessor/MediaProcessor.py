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
##from tqdm import tqdm   //导致进度条顺序打印
##from tqdm import trange
from xpinyin import Pinyin
##from moviepy.editor import  VideoFileClip
##from moviepy.editor import *
##from pymediainfo import MediaInfo
##from pprint import pprint
import atpbar
from atpbar import flush

## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
## 坑爹的pycache, 不会更新，第一次的值如果保留，后面就会一只是用原来的值，所以要删除
os.unsetenv('TZ')
from filemanager.FileManager import FileManager


class MediaAttribute( object ):
    def GetMediaAttribute( self, mediaPath ):
        ''' must conside file name has  - space. '''
        cmd = 'ffprobe -v quiet -show_streams -print_format json \"%s\"' %  mediaPath
        output = subprocess.getoutput( cmd )
        ''' Fuck this output'''
        output = output.replace( 'Active code page: 65001', '' )
        json_data = json.loads(output)
        if not 'streams' in json_data:
            print( '  <** Get Media info Failed: %s' % mediaPath )
            self.mediaPath      = mediaPath
            self.codec_name     = ''
            self.codec_type     = ''
            self.width          = 0
            self.height         = 0
            self.avg_frame_rate = ''
            self.duration       = ''
        else:
            try:
                self.mediaPath      = mediaPath 
                self.codec_name     = json_data['streams'][0]['codec_name'] 
                self.codec_type     = json_data['streams'][0]['codec_type']
                self.width          = json_data['streams'][0]['width'] 
                self.height         = json_data['streams'][0]['height'] 
                self.avg_frame_rate = json_data['streams'][0]['avg_frame_rate'] 
                self.duration       = json_data['streams'][0]['duration'] 
            except:
                self.mediaPath      = mediaPath 
                self.codec_name     = json_data['streams'][1]['codec_name'] 
                self.codec_type     = json_data['streams'][1]['codec_type']
                self.width          = json_data['streams'][1]['width'] 
                self.height         = json_data['streams'][1]['height'] 
                self.avg_frame_rate = json_data['streams'][1]['avg_frame_rate'] 
                self.duration       = json_data['streams'][1]['duration'] 


    def __init__( self, mediaPath ):
        self.mediaPath      = mediaPath
        self.codec_name     = ''
        self.codec_type     = ''
        self.width          = 0
        self.height         = 0
        self.avg_frame_rate = ''
        self.duration       = ''
        self.GetMediaAttribute( mediaPath )


class UidDirSizeInfo( object ):
    def __init__( self, uidDir ):
        self.classDir               = [ 'A\\', 'B\\', 'C\\', 'D\\' ]
        self.uidDir                 = uidDir
        self.videoSizeOkPath        = [ ]
        self.needResizeVideoPath    = [ ]
        self.videoTargetWidth       = 720
        self.videoTargetHeight      = 1280
        self.uidDirSizeInfo         = {  } ## { '3xxx\\': {ok:[], notok:[] }    }
        self.CheckVideoSizeInDir( self.uidDir )

    ''' check videos in A/B/C/D.'''
    def CheckVideoSizeInDir( self, path ):
        sizeOk = {  }
        videos = [  ]
        pathA, pathB, pathC, pathD = [ path + x for x in self.classDir ]
        if os.path.exists( pathA ):
            videos = videos + [ pathA + x for x in os.listdir( pathA ) ]
        if os.path.exists( pathB ):
            videos = videos + [ pathB + x for x in os.listdir( pathB ) ]
        if os.path.exists( pathC ):
            videos = videos + [ pathC + x for x in os.listdir( pathC ) ]
        if os.path.exists( pathD ):
            videos = videos + [ pathD + x for x in os.listdir( pathD ) ]
        for vid in videos:
            videoPath = vid
            mediaAttribute = MediaAttribute( videoPath )
            if ( mediaAttribute.width  == self.videoTargetWidth  ) and \
               ( mediaAttribute.height == self.videoTargetHeight ):
                self.videoSizeOkPath.append( videoPath ) 
            else:
                videoSizeX = mediaAttribute.width
                videoSizeY = mediaAttribute.height
                videoAttr  = ( videoPath, videoSizeX, videoSizeY )
                self.needResizeVideoPath.append( videoAttr )
        sizeOk = { 'sizeOk':self.videoSizeOkPath, 'sizeNotOk':self.needResizeVideoPath }
        self.uidDirSizeInfo[path] = sizeOk


class VideoResizer( object ):
    def __init__( self, videoPath, x, y ):
        print( '  <** Init VideoReszier...On: %s .>' % videoPath )
        self.videoPath      = videoPath
        self.targetX        = 720
        self.targetY        = 1280
        self.targetPath     = ''
        self.moveToDir      = ''
        self.newPath        = ''
        self.x              = x
        self.y              = y
        self.cropx          = 0
        self.cropy          = 0
        self.cmd            = ''
        self.recursion      = False
        self.targetDir      = ''
        self.GenTargetPath( ) 
        self.tmpPath        = ''
        self.ResizeVideo( self.videoPath, self.x, self.y )

    def GenTargetPath( self ):
        slices = self.videoPath.split( '\\' )
        self.moveToDir = '\\'.join( self.videoPath.split('\\mp4\\')[0:-1] ) + '\\bad_org\\'
        ##self.moveToDir = '\\'.join( slices[0:-2] ) + '\\bad_org\\' 
        filename = slices[-1]
        self.newPath   = self.moveToDir +  filename
        if not os.path.exists( self.moveToDir ):
            os.makedirs( self.moveToDir )

        newFilename = slices[-1].split('.')[0] + '_'+str( random.randint(10,99) ) + '.mp4'
        self.targetDir  = '\\'.join( slices[0:-1] ) + '\\'
        self.targetPath = self.targetDir + newFilename 

    ''' move bad video to bad_org dir'''
    def MoveBadVideo( self, videoPath ):
        if not os.path.exists( self.newPath ):
            shutil.move( videoPath, self.newPath )

    ''' real resize.'''
    def ResizeVideo( self, videoPath, x, y ):
        print( '  <**** Resize - %s -%d  -%d  .>' % (videoPath,self.x,self.y) )
        ''' 662 ** 1280 '''
        ##self.x = x 
        ##self.y = y
        if ( self.x < self.targetX ) and ( self.y <= self.targetY ):
            scalex = round( float(self.targetX)/ self.x, 3 )
            scaley = round( float(self.targetY)/ self.y, 3 )
            if scalex == scaley:
                ''' 等比缩放 '''
                scalex_to  = round( scalex * self.x )
                scaley_to  = round( scaley * self.y )
                self.cmd   = 'ffmpeg -hide_banner -v quiet -stats -i %s -vf scale=%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                            %( videoPath, scalex_to, scaley_to, self.targetPath )
                print('  <** -1: EqualScale: %s .>' % self.cmd )
                os.system( self.cmd )
            else:
                ''' 不是等比，需要缩放后裁剪  480 x 640 -> 1.5 = 720x960 '''
                yto = round( float(self.targetY)/y, 3 )
                xto = round( float(self.targetX)/x, 3 )
                tmp = self.targetPath + '_tmp.mp4'
                if xto > yto:
                    self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=720:-2 -preset slow  -crf 20 %s 2>&1 ' \
                    %(videoPath,  tmp)
                    print('  <** -1-1: ScaleLarge: %s .>' % self.cmd )
                    os.system(self.cmd)
                if xto < yto:
                    self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=-2:1280 -preset slow  -crf 20 %s 2>&1 ' \
                    %(videoPath,  tmp)
                    print( '  <** -1-2: ScaleLarge: %s .>' % self.cmd )
                    os.system( self.cmd )

                ''' 对视频进行裁剪 '''
                tmpAttribute = MediaAttribute( tmp )
                tmpX = tmpAttribute.width
                tmpY = tmpAttribute.height
                ''' 原来的处理：480x640 缩放之后是 720 960， 还是不能裁剪，直接就原图放进去了'''
                ''' X缩放倍数大于Y的，所以Y必然大于1280'''
                cropx = 0
                cropy = 0
                if tmpX == '720':
                    cropy = round( (tmpY - self.targetY)/2 )
                    cropx = 0
                ''' Y缩放倍数大于X，所以X必然大于720'''
                if tmpY ==1280:
                    cropy = 0
                    cropx = round( (tmpX - self.targetX)/2 )

                self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                    %( tmp, self.targetX, self.targetY, cropx,  cropy, self.targetPath )

                if os.path.exists( tmp ):
                    print( '  <** -1-2: Crop: %s .>'% self.cmd )
                    os.system( self.cmd )
                    os.unlink( tmp )
                else:
                    print( '  <** -1-2: Crop: ....not found file: %s .>' % tmp )


        ''' 给的高比规定的要大的时候，切掉多余的高 '''
        if ( x >= self.targetX ) and ( y >= self.targetY ):
            scalex = round( float(x)/self.targetX, 3 )
            scaley = round( float(y)/self.targetY, 3 )

            if scalex == scaley:
                scalex   = round( float(1)/scalex, 3 )
                self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=iw*%f:-2 -preset slow  -crf 20 %s 2>&1 ' \
                  %( videoPath, scalex, self.targetPath )
                print( '  <** -3-1: EqualReduce: %s .>' % self.cmd )
                os.system( self.cmd )
            else:
                tmp      = self.targetPath + '_tmp.mp4'
                self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=iw*%d:-2 -preset slow  -crf 20 %s 2>&1 ' \
                  %( videoPath, scalex, tmp )
                print( '  <** -3-2-1: Reduce: %s .>' % self.cmd )
                os.system( self.cmd )

                if os.path.exists( tmp ):
                    mediaAttribute = MediaAttribute( tmp )
                    tmpY = mediaAttribute.height
            
                    cropx = 0
                    gap   = tmpY - self.targetY
                    if gap > 0:
                        cropy = round(gap/2)
                    else:
                        cropy = 0

                    self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                      %( tmp, self.targetX, self.targetY, cropx,  cropy, self.targetPath )
                    if os.path.exists( tmp ):
                        print( '  <**-3-2-2: Crop: %s .>' % self.cmd )
                        os.system( self.cmd )
                        os.unlink( tmp )
                    else:
                        print('  <**-3-2-2: Crop: file not found: %s' % tmp )

        ''' 恒屏的裁切, 直接旋转得了，不截了ffmpeg -i a.mp4 -vf "vflip" /b.mp4. vflip 即表示垂直翻转.  '''
        ''' transpose=0，表示：逆时针旋转90度并垂直翻转  '''
        ''' transpose=1，表示：顺时针旋转90度  '''
        ''' transpose=2，表示：逆时针旋转90度  '''
        ''' transpose=3，表示：顺时针旋转90度后并垂直翻转. '''
        if ( x >= self.targetX ) and ( y < self.targetY ) and ( x > y ):
            tmp = self.targetPath + '_tmp.mp4'
        
            self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf transpose=1 -preset slow  -crf 20 %s 2>&1 ' \
                    % ( videoPath, tmp )
            print(' <** -4-1: Rotate: %s .>' % self.cmd )
            os.system( self.cmd )
            mediaAttribute = MediaAttribute( tmp )
            tmpX = mediaAttribute.width
            tmpY = mediaAttribute.height
            if os.path.exists( tmp ):
                self.recursion = True
                print('  <** ->4-2: CallBack: %s :[ %d * %d ]\n' % ( tmp, tmpX, tmpY ) )
                self.tmpPath = videoPath
                ##ReturnTmp = self.ResizeVideo( tmp, tmpX, tmpY )
                self.x = tmpX
                self.y = tmpY
                self.ResizeVideo( tmp, tmpX, tmpY )

                self.targetPath = tmp
                self.recursion  = False

        """ 720 x 960 的视频 会造成死循环,旋转得到 960x720，又是横屏，又旋转
        补充处理这种视频，直接放大，裁剪        
        """
        if ( x >= self.targetX ) and ( y < self.targetY ) and( x < y ):
            tmp = self.targetPath + '_tmp.mp4'
            self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf scale=-2:1280 -preset slow  -crf 20 %s 2>&1 ' \
                  % ( videoPath, tmp )
            print('  <** -5-1: Scale: %s .>'% self.cmd )
            os.system( self.cmd )

            mediaAttribute = MediaAttribute( tmp )
            tmpX = mediaAttribute.width 
            cropx = round( (tmpX - self.targetX)/2 )
            cropy = 0
            self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s  -vf crop=%d:%d:%d:%d -preset slow  -crf 20 %s 2>&1 ' \
                %( tmp, self.targetX, self.targetY, cropx,  cropy, self.targetPath)

            if os.path.exists( tmp ):
                print('  <** -5-2: Crop: %s .>' % self.cmd )
                os.system( self.cmd )
                os.unlink( tmp )
            else:
                print('  <** -5-2: Crop: not found: %s .>' % tmp )

        '''处理完的视频，将原有的挪走到指定位置，备用'''
        if self.recursion == False:
            self.MoveBadVideo( videoPath )
            ##self.tmpPath = videoPath  ## 递归的时候，重命名回原来的文件会引起报错。
            print(self.tmpPath)
            print(self.targetPath)
            shutil.move( self.targetPath, videoPath )
            ##shutil.move( self.targetPath, self.tmpPath )
        

class MediaProcessor( object ):
    def __init__( self, srcDir, dstDir, pmax, operate, platform ):
        ''' 这里初始化每个属性之后不能带 ','， 否则参数变元组 '''
        self.srcDir     = srcDir  
        self.dstDir     = ''
        self.pmax       = pmax
        self.operate    = operate
        self.platform   = platform
        self.concatFlag = 'dd.txt'
        self.srtDir     = ''
        self.clipOutDir = ''
        self.clipOperateParams = [ ]

        self.fm = FileManager(
            srcDir          = srcDir,
            dstDir          = dstDir,
            operate         = '',
            platform        = '',
            fileManagerData = '',
            password        = '' 
        )

        self.needConcatUidDir       = [ ]
        self.needConcatVideoDir     = [ ]
        self.mtsFilePath            = [ ]
        self.dirInfo                = {  }  ## { file\mp4: { sizeok: [ file1.mp4], sizenotok: [file2.mp4] }}
        self.uidMtsFiles            = {  }  ## {  name1: [1.ts,2.ts,3.ts], name2:[3.ts, 4.ts] }
        self.encodeFlag             = 'Concat_'
        self.subDirContainTS        = [ ]

        print('-------------------mediaprocessor---------------------')
        print('srcDir:', self.srcDir)
        print('dstDir:', self.dstDir)
        print('operate:',self.operate)
        print('platform',self.platform)
        print('-------------------me----end---------------------')

    ''' get all need concat video dirs, dir in clude 'dd.txt. '''
    def GetNeedConcatVideoDir( self ):
        self.fm.GetAllFiles( self.srcDir, recursion=True )
        for p in self.fm.allDirs:
            flagPath = p + self.concatFlag
            if os.path.exists( flagPath ):
                self.needConcatUidDir.append( p )
    
    ''' get all mp4 files of path, path come from needConcat.'''
    def GetAllMp4DirsOfNeed( self, path ):
        videoDir = path + 'video\\'
        if not os.path.exists( videoDir ):
            videoDir = path + 'mp4\\'
        if not os.path.exists( videoDir ):
            print( '  <* %s not include valid video dir. >' % videoDir )
        else:
            self.needConcatVideoDir.append( videoDir )

    ''' resize not ok video in uidDir. '''
    def ResizeVideoSizeBad( self, vpath ):
        print( '  <*** - ResizeUnder: %s .>' % vpath )
        uidDirInfo = UidDirSizeInfo( vpath )

        ''' { vpath: { sizeOk:[], sizenotOk:[] }'''
        for bad in  uidDirInfo.uidDirSizeInfo[vpath]['sizeNotOk']:
            badVideoPath = bad[0]
            badVideoX    = bad[1]
            badVideoY    = bad[2]
            resizer = VideoResizer( badVideoPath, badVideoX, badVideoY )
            uidDirInfo.uidDirSizeInfo[vpath]['sizeOk'].append( badVideoPath )
        self.dirInfo[vpath] =  uidDirInfo.uidDirSizeInfo[vpath] 

    ''' class size ok or not, save them to sizeOK, needresize list.'''
    def GetClassificationBySize( self ):
        self.needConcatUidDir   = [ ]
        self.needConcatVideoDir = [ ]
        self.GetNeedConcatVideoDir( )    ## /3xxx/ -> dd.txt
        for needDir in self.needConcatUidDir:
            self.GetAllMp4DirsOfNeed( needDir )  ## get 3xxx/mp4
        for vpath in self.needConcatVideoDir:   ##  3xxx/mp4/
            self.ResizeVideoSizeBad( vpath )
            
    ''' convert file to mts. will be convenience to concat. '''
    def ConvertMediaToMts( self, path ):
        mediaAttribute = MediaAttribute( path ) 
        tsfilePath = path + '_.mts'
        if 'h264' in mediaAttribute.codec_name:
            self.cmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s -q 0   %s' \
                        % ( path, tsfilePath )
        elif 'hevc' in mediaAttribute.codec_name:
            self.cmd = 'ffmpeg -hide_banner  -v quiet -stats -i %s -q 0   %s' \
                % ( path, tsfilePath )
        else:
            print( '  <E** - Unknow Codec: %s .>' % path )
        self.mtsFilePath.append( tsfilePath )
        os.system( self.cmd )
        return self.mtsFilePath

    ''' merge mts list to single file. '''
    def MergeMtsToFile( self, mp4RootDir, mtslist ):
        mtslist.sort( )
        ffmpegInputFile = mp4RootDir + 'mts_lst.txt'
        outname         = 'Concat_' + str( random.randint(100,999) ) + str(random.randint(10,99)) + '.mp4'
        outputFile      = mp4RootDir  + outname
        if os.path.exists( ffmpegInputFile ):
            os.unlink( ffmpegInputFile )

        longStrings = ''
        for mts in mtslist:
            line = 'file  \'%s\'\n' % mts 
            longStrings = longStrings + line
        
        self.fm.Writer( longStrings, ffmpegInputFile, 'w+' )
        ##self.cmd = 'ffmpeg -hide_banner -v quiet  -f concat -safe 0 -i %s -c copy  %s' \
        self.cmd = 'ffmpeg -hide_banner -v quiet -stats  -f concat -safe 0 -i %s -c copy  %s' \
                    % ( ffmpegInputFile, outputFile )
        print( '  <** - Merge: %s .> ' % self.cmd )
        os.system( self.cmd )
             
    ''' convert ok video to mts. use mutil thread. '''
    def ConvertAllOkVideoToMts( self ):
        for vpath in self.dirInfo.keys( ):
            mp4RootDir = '\\'.join( vpath.split('\\')[0:-2] ) + '\\'
            okvideos = self.dirInfo[vpath]['sizeOk']
            mtslist = [ ]
            threads = [ ]
            for vid in okvideos:
                t = threading.Thread( target=self.ConvertMediaToMts, args=[vid] )
                t.setName( '    <** - ConvertTomts: %s .>' % vid )
                threads.append( t )
                mts = vid + '_.mts'
                mtslist.append( mts )
            for t in threads:
                t.deamon = True
                t.start( )
                print( t.getName() )
                while True:
                    if len( threading.enumerate() ) < 3:
                        break
            for t in threads:
                t.join( )

            self.uidMtsFiles[mp4RootDir] = mtslist

    ''' multil thread merge mts. '''
    def MutilThreadMerge( self ):
        threads = [ ]
        n = 1
        for uidDir in self.uidMtsFiles.keys():
            threadname = '%03d' % n
            mp4RootDir = uidDir
            mtslist    = self.uidMtsFiles[ uidDir ]
            ##self.MergeMtsToFile( mp4RootDir, mtslist )
            t = threading.Thread( target=self.MergeMtsToFile, args=[ mp4RootDir, mtslist] )
            t.setName( '\t<** Thread - %s : Merge at: %s' % ( threadname, mp4RootDir ) )
            n = n + 1
            threads.append( t )

        for t in threads:
            t.deamon = True
            t.start( )
            print( t.getName() )
            while True:
                if len( threading.enumerate() ) < 2:
                    break
        for t in threads:
            t.join()

        for uidDir in self.uidMtsFiles.keys( ):
            mtslist = self.uidMtsFiles[ uidDir]
            for mts in mtslist:
                if os.path.exists( mts ):
                    os.unlink( mts )

    ''' encode a single media file. '''
    def EncodeSingleMediaFile( self, path ):
        slices = path.split( '\\')
        outDir = '\\'.join( slices[0:-1] ) +  '\\'
        filename = ''.join( slices[-1].split( '.' )[0:-1] )
        outFile = outDir + 'Compress_' + filename +'.mp4'
        self.cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -c:v libx264 -acodec  copy  -crf 20 -preset:v veryslow %s' \
                    % ( path, outFile )
        ''' self.logger.write. '''
        print( '  <** - %s .>' % self.cmd )
        os.system( self.cmd )


    ''' encode concated mp4 file with ffmpeg  h.264, with mutil threads. '''
    def EncodeConcatedVideos( self ):
        self.pmax = 3
        print('  <** - Search Media Files..... .> ')
        self.fm.GetAllFiles( self.srcDir, recursion=True )
        allMediaFiles = self.fm.allFiles
        needEncodeMedias = [ ]

        for media in allMediaFiles:
            if ( 'Concat_' in media ) and ( self.fm.IsMIMEType( media, 'video') ):
                needEncodeMedias.append( media )

        threads = [ ]
        for media in needEncodeMedias:
            t = threading.Thread( target=self.EncodeSingleMediaFile, args=[ media ] )
            t.setName( '  <**** Thread - %s: encoding...... >' % media )
            threads.append( t )

        for t in threads:
            t.deamon = True
            t.start()
            print( t.getName() )
            while True:
                if len( threading.enumerate() ) < self.pmax:
                    break
        for t in threads:
            t.join( )


    ''' convert single flv to  mp4. '''
    def ConvertSingleFlvToMp4( self, path ):
        slices = path.split( '\\')
        outDir = '\\'.join( slices[0:-1] ) +  '\\'
        filename = ''.join( slices[-1].split( '.' )[0:-1] )
        outFile = outDir + filename +'.mp4'
        if os.path.exists( outFile ):
            outFile = outDir + filename + '_' + str(random.randint(10,99)) + '.mp4'
        
        ##print( '  <** -Convert-> flv: %s  -> %s  .>' % (path, outFile) )
        ret = subprocess.call( [ 'ffmpeg', '-hide_banner', '-v', 'quiet', '-stats', '-i',
                                 path, '-ar', '44100', '-ac', '2', '-vcodec', 'copy', outFile],
                                 ##stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT 
                             )
        print( '  <**** -Delete-Flv: %s' % path )
        os.unlink( path )


    ''' convert all flvs to mp4. '''
    def ConvertAllFlvsToMp4( self ):
        self.pmax = 5
        print('  <** - Search flv Files..... .> ')
        self.fm.GetAllFiles( self.srcDir, recursion=True )
        allFiles = self.fm.allFiles

        flvs = [ ]
        for flv in allFiles:
            if ( '.flv' in flv ) and ( self.fm.IsMIMEType( flv, 'flv' ) ):
                flvs.append( flv )

        threads = [ ]
        for flv in flvs:
            ##self.ConvertSingleFlvToMp4( flv )
            t =threading.Thread( target=self.ConvertSingleFlvToMp4, args=[flv] )
            t.setName( '  <** - Thread -Convert: %s .>' % flv )
            threads.append( t )

        for t in threads:
            t.setDaemon = True
            t.start( )
            print( t.getName() )
            while True:
                if ( len(threading.enumerate()) ) < self.pmax:
                    break
        for t in threads:
            t.join( )


    ''' clip single video. '''
    ''' oplist = [ srt, video, ss, to, outfile ] '''
    def ClipSingleVideo( self, operateParam=[] ):
        videoFile = operateParam[1]
        start     = operateParam[2]
        end       = operateParam[3]
        outFile   = operateParam[4]

        """
        print( '  <** - Clip: %s %s %s %s .>' % 
               (videoFile, start, end, outFile )    
             )
        """
        ret = subprocess.call( [ 'ffmpeg', '-hide_banner', '-ss', start, 
                                 '-to', end, '-i', videoFile, '-c', 'copy', outFile ], 
                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT )

        """
        p =  subprocess.Popen([bash_path, ffmpeg_path, "-hide_banner", "-ss", op[2], "-to", op[3], \
                                                   "-i", op[1], "-c", "copy", op[4] ], \
        stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()
        """

    ''' get operate list from srt file and video file. '''
    def GetOperateList( self, srtDir ):
        srtList         = os.listdir( srtDir )
        srtFiles        = [ ]
        srtFileInfos    = [ ]  ## [ (srtfile, srtname, videoname) ]

        for srt in srtList:
            srtFile = srtDir + srt
            vidFile = ''
            vidname = ''
            if os.path.isfile( srtFile ) and ( srtFile[-4:]=='.srt' ):
                vidFile = srtFile.replace( '.srt', '.mp4' )
                if os.path.isfile( vidFile ):
                    vidname = srt.replace( '.srt', '' )
                    srtFileInfos.append( (srtFile, vidFile, vidname) )
        
        for info in srtFileInfos:
            srtFile   = info[0] 
            vidFile   = info[1] 
            vidname   = info[2] 
            lines     = self.fm.Reader( srtFile )
            clipCount = 0
            for line in lines:
                line = line.strip('\n')
                if '-->' in line:
                    clipCount = clipCount + 1
                    ss        = line.split(',')[0]
                    tt = line.split(',')[1].split('>')[1].split(',')[0].strip(' ')
                    namesuf = '%03d' % clipCount
                    outFile = self.clipOutDir + vidname + '_' + namesuf + '.mp4'
                    if os.path.exists( outFile ):
                        namesuf = namesuf + str( random.randint(10,99) )
                        outFile = self.clipOutDir + vidname + '_' + namesuf + '.mp4'
                    self.clipOperateParams.append( [srtFile, vidFile, ss, tt, outFile] )

    ''' clip video from srt files. '''
    def GetAwesomeClipsFromSrt( self ):
        self.GetOperateList( self.srtDir )
        self.pmax = 4
        threads =  [ ]
        for oplist in self.clipOperateParams:
            t =threading.Thread( target=self.ClipSingleVideo, args=[oplist] )
            t.setName( '  <** - Thread -Clip: %s | %s | %s | %s .>' % (oplist[1], oplist[2], oplist[3], oplist[4]) )
            threads.append( t )

        for t in threads:
            t.setDaemon = True
            t.start( )
            print( t.getName() )
            while True:
                if ( len(threading.enumerate()) ) < self.pmax:
                    break
        for t in threads:
            t.join( )


    ''' merge playback ts file to mp4. '''
    def MergePlayBackTS( self, path ):
        tsListFile = path + 'file.list'
        outFile    = path + 'merge_' + str(random.randint(10,99)) + '.mp4'
        strings    = ''
        tsFiles    = os.listdir( path )
        tsFiles.sort( reverse=False )
        for tsFile in tsFiles:
            tsPath = path + tsFile
            if ( os.path.isfile(tsPath) ) and  ( os.path.getsize(tsPath) > 0)\
                                          and  ( tsFile[-3:] == '.ts' ):
                line = 'file \'%s\'\n' % tsPath
                strings = strings + line
        self.fm.Writer( strings, tsListFile, 'w+' )
        cmd = 'ffmpeg -hide_banner -v quiet -stats -f concat  -safe 0 -i %s -c copy %s' % \
              ( tsListFile, outFile )
        print( '  <** - Merge paly back TS: %s .>' % path )
        os.system( cmd )
        os.unlink( tsListFile )

    ''' IsDirContainTS. '''
    def IsDirContainTS( self, path ):
        files = os.listdir( path )
        for _file in files:
            filePath = path + _file
            if filePath[-3:] == '.ts':
                return True
        return False


    ''' find all subdir contain ts. save them to self.subDirContainTS. '''
    def FindSubDirContainTS( self, path ):
        self.fm.GetAllFiles( path, recursion=True )
        for _dir in self.fm.allDirs:
            if self.IsDirContainTS( _dir ):
                self.subDirContainTS.append( _dir )

    ''' find all subdir contain ts, merge them. '''
    def MergePlayBackTSDirs( self, path ):
        self.pmax = 3
        self.FindSubDirContainTS( path )
        for _dir in self.subDirContainTS:
            self.MergePlayBackTS( _dir )


            
    ''' choose what should to be done. '''        
    def ChooseWhatToDo( self ):
        if ( self.operate=='concat-video' ) and ( self.platform=='mediaprocessor' ):
            self.GetClassificationBySize( )
            self.ConvertAllOkVideoToMts( )
            self.MutilThreadMerge( )
        if ( self.operate=='encode' ) and ( self.platform=='mediaprocessor' ):
            self.EncodeConcatedVideos( )

        if ( self.operate=='convert-flv' ) and ( self.platform=='mediaprocessor' ):
            if os.path.isdir( self.srcDir ):
                self.ConvertAllFlvsToMp4( )
            elif os.path.isfile( self.srcDir ) and self.fm.IsMIMEType( self.srcDir, 'flv' ):
                print( '  <** -Convert-Flv: %s .>' % self.srcDir )
                self.ConvertSingleFlvToMp4( self.srcDir )
            else:
                print( '  <** Input: %s invalid.' % self.srcDir )
        if ( self.operate=='clip-srt' ) and ( self.platform=='mediaprocessor'):
            self.srtDir   = self.srcDir
            self.clipOutDir = self.srtDir + 'outclip\\'
            if not os.path.exists( self.clipOutDir ):
                os.makedirs( self.clipOutDir )
            self.GetAwesomeClipsFromSrt( )
        if ( self.operate=='merge-ts' ) and ( self.platform=='mediaprocessor'):
            if self.IsDirContainTS( self.srcDir ):
                self.MergePlayBackTS( self.srcDir )
            else:
                self.MergePlayBackTSDirs( self.srcDir )
 
    def Run( self ):
        self.ChooseWhatToDo( )

         
