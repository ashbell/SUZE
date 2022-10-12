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
from pymediainfo import MediaInfo
from pprint import pprint
import mimetypes
import easyocr
import cv2
import face_recognition as FR
import numpy 
import copy

from mediaprocessor.MediaProcessor import MediaAttribute
from filemanager.FileManager       import FileManager
from facer.QueryHeaders       import QueryHeaders


## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')

class Facer( object ):
    def __init__( self, srcDir, operate, platform ):
        self.srcDir         = srcDir
        self.operate        = operate
        self.platform       = platform
        self.pmax           = 5

        self.fm = FileManager(
            srcDir          = self.srcDir,
            dstDir          = '',
            operate         = '',
            platform        = '',
            fileManagerData = '',
            password        = ''
        )
        self.imageCapPerSec = { }   ##  { mp4: [img1, img2,img3] } 
        self.sizeVideo      = { }   ##  { mp4: [x,y] }
        self.imageCrop      = { }   ##  { mp4: [lt, rb,mid, oldstart, oldendmid] }
        self.videoText      = { }   ##  { mp4: [text1, text2,......] }
        self.videoLegalText = { }
        self.videoHasText   = { }
        self.videoNoHasText = { }
        self.hasTextDir     = self.srcDir + 'has\\'
        self.noTextDir      = self.srcDir + 'no_has\\'
        self.uidFile        = os.getcwd( ) + '\\uidFile.uid'
        self.uidGotFile     = os.getcwd( ) + '\\uidGot.uid'
        self.uidInFile      = [ ]
        self.uidRead        = [ ]

        ''' d=''; for s in {A..Z}; do d=$d"'"$s"'",; done; echo $d  '''
        self.legalChars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z', \
               'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
               '0','1','2','3','4','5','6','7','8','9','_','-' ]

        self.logFile        = self.srcDir + '_OCR.ocr'
        self.ksPostQueryUrl = 'https://www.kuaishou.com/graphql'

        self.videoFrames    = { } ## vid: [pic1, pic2,pic3]
        self.videoFramesNpy = { } ## video: [npy1, npy2]
        self.threads        = [ ]


    ''' format  text string  that  get  from OCR. delete other chars. '''
    def FormatTextFromOCR( self, string ):
        result = [ ] 
        lst = list(string)
        for c in lst:
            if c in self.legalChars:
                result.append(c)
        return ''.join(result)
         
    ''' get text from img, return text tuple. '''
    def GetTextFromImage( self, img, videoPath ):
        ##print('gettext: ', img, )
        texts = ''
        reader = easyocr.Reader( ['ch_sim','en'], gpu=False,verbose=False )
        with open( img, 'rb' ) as f:
            imgData = f.read()
            texts  = reader.readtext( imgData )
        
        for text in texts:
            self.videoText[videoPath].append(text[1])

    ''' capture image per second from video file. default 1s, save image path list[] '''
    ''' capMethod = headTail, get 2 images, else get 1s of. '''
    def CaptureImagePerSecondFromVideo( self, video ):
        mediaAttr       = MediaAttribute( video )
        duration        = float( mediaAttr.duration )
        videoX          = int( mediaAttr.width )
        videoY          = int( mediaAttr.height )
        avgFrameRate    = int(mediaAttr.avg_frame_rate.split('/')[0])
        videoImg        = [ ]
        
        ''' short video, captrue head and tail. '''
        ##if 5 < duration < 60:
        if (5 < duration <= 180) and (avgFrameRate > 15 ):
            startImage = video + '_start.png'
            endImage   = video + '_end.png'
            startCmd = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i \"%s\" -f image2 -vf   fps=fps=1/1 -qscale:v 2 \"%s\"' \
                        %(1, 2, video, startImage)
            endCmd = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i \"%s\" -f image2 -vf   fps=fps=1/1 -qscale:v 2 \"%s\"' \
                        %(duration-1, duration, video, endImage)
            os.system( startCmd ) 
            os.system( endCmd )
            self.imageCapPerSec[video] = [ startImage, endImage ]
            self.sizeVideo[video]      = [ videoX, videoY ]
        
        else:
            self.imageCapPerSec[video] = [  ]
            self.sizeVideo[video]      = [ 720, 1280 ]
        """

        ''' merge video, capture per second. '''
        if 300 < duration < 600:
            dim = 1
            count = round( duration/int(dim) ) + 1
            for num in range(1, count):
                imagePath = '%s_%05d.png' % ( video, num )
                videoImg.append( imagePath )

            imgList = '%s_' % ( video )
            outImgList = imgList + '%05d.png'
            cmd = 'ffmpeg -nostats -loglevel 0  -y -i \"%s\" -f image2 -vf fps=fps=1/%d  \"%s\"' \
                % ( video, int(dim), outImgList )
            os.system(cmd)
            self.imageCapPerSec[video] = videoImg
            self.sizeVideo[video]      = [videoX, videoY]

        ##print(self.imageCapPerSec)
        ''' give up,  too short video. '''
        if duration < 5:
            self.imageCapPerSec[video] = [ ]
            self.sizeVideo[video] = [ 720, 1280 ]
        """

    ''' crop text area, easy to recogonize and faser. '''
    def CropTextAreaFromVideo( self, videoPath ):
        fullimgs =   self.imageCapPerSec[videoPath]
        sizeX    =   self.sizeVideo[videoPath][0]
        sizeY    =   self.sizeVideo[videoPath][1]
        self.imageCrop[videoPath] = [ ]

        ''' area: w:h: posx: posy '''
        for image in fullimgs:
            lt   = [ int(sizeX/2), int(sizeY/10), 0,  0 ]
            rb   = [ sizeX, int(sizeY/10), 0,  int(sizeY*0.9) ]
            oec  = [ sizeX, int(sizeY/2), 0, 0 ]
            ##lgc = [ x, 250, 0, 50]
            ##osc = [ 300, 120, (x-300)/2, y-120]
            ##oec = [ x, 250, 0, 50 ]
           
            ''' oec: old end center, osc: old start center.'''
            imglt   = image + '_lt.png'
            imgrb   = image + '_rb.png'
            imgoec  = image + '_oec.png'
            imglgc  = image + '_lgc.png'
            imgosc  = image + '_osc.png'
            
            ltCmd  = 'ffmpeg -nostats -loglevel 0  -y -i \"%s\" -filter:v \"crop=%d:%d:%d:%d\" \"%s\"' % \
                     (image, lt[0], lt[1], lt[2], lt[3], imglt)
            rbCmd  = 'ffmpeg -nostats -loglevel 0  -y -i \"%s\" -filter:v \"crop=%d:%d:%d:%d\" \"%s\"' % \
                     (image, rb[0], rb[1], rb[2] , rb[3], imgrb)
            oecCmd = 'ffmpeg -nostats -loglevel 0  -y -i \"%s\" -filter:v \"crop=%d:%d:%d:%d\" \"%s\"' % \
                     (image, oec[0], oec[1], oec[2], oec[3], imgoec)
            os.system( ltCmd )
            os.system( rbCmd )
            os.system( oecCmd )
            self.imageCrop[videoPath].append( imglt )
            self.imageCrop[videoPath].append( imgrb )
            self.imageCrop[videoPath].append( imgoec )
        ##print(self.imageCrop)

    ''' single video run. '''            
    def SingleVideoProcess( self, vid ):
        self.GetTextFromVideo( vid )
        self.CleanAllOfVideo( vid )
        self.WriteResultToLog( vid )


    ''' get id text from video dir. '''
    def GetTextFromVideoDir( self, path ):
        self.fm.GetAllFiles( path, recursion=True )
        videos = [ ]
        for _file in self.fm.allFiles:
            if _file[-4:] =='.mp4':
                videos.append( _file )
        for vid in videos:
            self.GetTextFromVideo( vid )
            self.CleanAllOfVideo( vid )
            self.WriteResultToLog( vid )
            self.SplitVideosToDir( vid )
            print('==========================================')
                            
   
    ''' write result to logfile. '''
    def WriteResultToLog( self, path ):
        logStr = path + ': '
        strings = self.videoLegalText[path]
        for string in strings:
            logStr = logStr + string + ' -> '
        logStr = logStr + '\n'
        self.fm.Writer( logStr, self.logFile, 'a+' )


    ''' clean all pngs. '''
    def CleanAllOfVideo( self, path ):
        starEndImages = self.imageCapPerSec[path]
        cropImages    = self.imageCrop[path]

        for img in starEndImages:
            if os.path.exists( img ):
                os.unlink( img )
        for img in cropImages:
            if os.path.exists( img ):
                os.unlink( img )
        
    ''' get id text from single video.'''
    def GetTextFromVideo( self, path ):
        self.pmax = 5
        self.CaptureImagePerSecondFromVideo( path )
        self.CropTextAreaFromVideo( path )
        self.videoText[path] = [ ]
        images = self.imageCrop[path]
        for image in images:
            print( '  <** - GetTextFromImage: %s ' % image)
            self.GetTextFromImage( image, path )
            """
            t = threading.Thread( target=self.GetTextFromImage, args=[image, path])
            t.setName( '  <** - Detect Text: %s : %s.>' % (path, image) )
            self.threads.append( t )
            """
        ##print(threads)
        """
        for t in threads:
            t.deamon = True
            t.start()
            print( t.getName() )
            ##print(len(threading.enumerate()))
            while True:
                if len( threading.enumerate() )  < self.pmax:
                    break 
        for t in threads:
            t.join()
        """

        ##print(self.videoText)

        for path in self.videoText.keys():
            self.videoLegalText[path] = [ ]
            for _str in self.videoText[path]:
                ''' need to process space like: myname  Q '''
                slices = _str.split(' ')
                for string in slices:
                    legalStr = self.FormatTextFromOCR( string )
                    ''' for ks rule, name must more than 8 chars. '''
                    if len(legalStr) >= 8:
                        self.videoLegalText[path].append( legalStr )

    ''' write uid to file. self.uidFromVideo={}. '''
    def WriteUidToFile( self ):
        wstr = ''
        for video in self.videoLegalText.keys():
            string = '%s -> %s\n' % (video,self.videoLegalText[video] )
            wstr = wstr + string
        self.fm.Writer( wstr, self.uidGotFile, 'a+')

    ''' check the video has text or not. save them to dict. '''
    def IsVideoHasText( self, videoPath ):
        texts = self.videoLegalText[videoPath]  
        if len(texts) > 0:
            return True
        return False

    ''' move has/nohas to dir. '''
    def SplitVideosToDir( self, video ):
        texts = self.videoLegalText[video]
        if len(texts) > 0:
            self.videoHasText[video] = texts
            filename = video.split('\\')[-1]
            targetPath = self.hasTextDir + filename
            if not os.path.exists( targetPath ):
                print('move: ', video, ' -> ', targetPath)
                shutil.move( video, targetPath )

        else:
            self.videoNoHasText[video] = texts
            filename = video.split('\\')[-1] 
            targetPath = self.noTextDir + filename
            if not os.path.exists( targetPath ):
                print('move: ', video, ' -> ', targetPath)
                shutil.move( video, targetPath )

        """
        for video in self.videoLegalText.keys():
            texts = self.videoLegalText[video]
            if len(texts) > 0:
                self.videoHasText[video] = texts
            else:
                self.videoNoHasText[video] = texts

        for video in self.videoHasText.keys():
            filename = video.split('\\')[-1]
            targetPath = self.hasTextDir + filename 
            if not os.path.exists( targetPath ):
                shutil.move( video, targetPath )

        for video in self.videoNoHasText.keys():
            filename = video.split('\\')[-1] 
            targetPath = self.noTextDir + filename
            if not os.path.exists( targetPath ):
                shutil.move( video, targetPath )
        """

    ''' search string on webserver, return 1st result as uid. '''
    def SearchStringOnWebserver( self, string ):
        fail    = 0
        maxTry  = 3
        while fail < maxTry:
            try:
                header = QueryHeaders( string )
                r = requests.post( self.ksPostQueryUrl, headers=header.header, json=header.queryJson )
                data = json.loads( r.text )
                userId = data['data']['visionSearchUser']['users'][0]['user_id']
                userName = data['data']['visionSearchUser']['users'][0]['user_name']
                userInfo = '%s -- %s --%s\n' % ( string, userId, userName )
                self.fm.Writer( userInfo, self.uidFile, 'a+' )
                fail = 0
                ##print(userInfo)
                return 
            except:
                fail = fail + 1
                print(' \t\t<** - %s  - Search Failed! .>' % string)

        secs = random.randint(0, 5) + random.randint(6,9)
        time.sleep( secs ) 

    ''' read uid from file ,save to self.uidInFile. '''
    def ReadUidFromFile( self, uidFile ):
        lines = self.fm.Reader( uidFile )
        for line in lines:
            line = line.strip( '\n' )
            if '->' in line:
                uids = line.split('->')[1]
                uids = uids.replace('\'', '').replace('[', '').replace(']', '').replace(' ', '')
                slices = uids.split(',')
                for _str in slices:
                    if len(_str) >= 8:
                        self.uidRead.append( _str )
            else:
                pass
                """
                if len( line ) >= 8:
                    self.uidRead.append( line )
                """
        ''' unique list elements. '''
        self.uidRead = list(set(self.uidRead))


    ''' search string on webserver from uid-file. use multi threads. '''
    def SearchStringOnWebserverFromFile( self, uidFile ):
        self.pmax = 2
        self.ReadUidFromFile( uidFile )
        threads = [ ]
        n = 0 
        ##print(self.uidRead)
        for uid in self.uidRead:
            t = threading.Thread( target=self.SearchStringOnWebserver, args=[uid])
            t.setName( '    <** - ThreadSearch-%03d:  %s' % (n,uid ))
            threads.append( t )
            n = n + 1
        for t in threads:
            t.deamon = True
            t.start()
            print( t.getName() )
            while True:
                if len( threading.enumerate() )  < self.pmax:
                    break
        for t in threads:
            t.join()

    ''' calculate the eigneVaule of single pictures. '''
    def CalculateEigenValueOfSinglePic( self, img ):
        imgLoad = FR.load_image_file( img )
        npyFile = img + '_FR.npy'

        if os.path.exists( npyFile ):
            return npyFile 

        try:
            npyData = FR.face_encodings( imgLoad )[0] #获得128维特征值
            numpy.savetxt( npyFile, npyData )
        except:
            print('    <** - FR: Failed to calc EigenValue: %s' % img )
            npyFile = ''
        return npyFile


    ''' get 3 frames of video. start at: 3s. save png path in self.videoFrames={} '''
    def GetFramesOfVideo( self, path ):
        self.videoFrames[path] = [ ]
        frameStart = 3
        frameCent  = frameStart + 1
        frameEnd   = frameCent  + 1
        
        pngStart = path + '_start.png'
        pngCent  = path + '_cent.png'
        pngEnd   = path + '_end.png'

        cmdStart = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(frameStart, frameCent, path, pngStart )
        cmdCent  = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(frameCent, frameEnd, path, pngCent )
        cmdEnd   = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(frameEnd, frameEnd+1, path, pngEnd )

        if not ( os.path.exists(pngStart) and os.path.exists(pngStart + '_FR.npy') ):
            os.system( cmdStart )
        if not ( os.path.exists(pngCent)  and os.path.exists(pngCent + '_FR.npy') ):
            os.system( cmdCent )
        if not ( os.path.exists(pngEnd)   and os.path.exists(pngEnd + '_FR.npy') ):
            os.system( cmdEnd )
        self.videoFrames[path].append( pngStart )
        self.videoFrames[path].append( pngCent )
        self.videoFrames[path].append( pngEnd )

    ''' recognize single video file. return vaule of it. save it in self.videoFrames={} ## vid:[png1,png2] '''
    ''' get 3 frames in video, use them to caculate  values. '''
    def RecognizeSingleVideo( self, path ):
        self.GetFramesOfVideo( path )
        for video in self.videoFrames.keys():
            self.videoFramesNpy[video] =  [ ]
            frames = self.videoFrames[video]
            for png in frames:
                videoNpy = self.CalculateEigenValueOfSinglePic( png )
                self.videoFramesNpy[video].append( videoNpy )
        
        for video in self.videoFramesNpy.keys():
            print(video, self.videoFramesNpy[video])

            
    ''' gen npy file from dir. get npydata file of every video. '''
    def GenNpyFromDir( self, path ):
        allVideos = [ ]
        print( '  <Scan-Videos: %s .>' % path )
        self.fm.GetAllFiles( path, recursion=True ) 
        for video in self.fm.allFiles:
            ##if self.fm.IsMIMEType(video, 'video'):
            if video[-4:] == '.mp4':
                allVideos.append( video )

        for video in allVideos:
            print( '   <** - Get Frames of: %s .>' % video )
            self.GetFramesOfVideo( video )

        for video in self.videoFrames.keys():
            self.videoFramesNpy[video] = [ ]
            print( '\t<** - Get Eigen of: %s........>' % video )
            frames = self.videoFrames[video]
            for png in frames:
                videoNpy = self.CalculateEigenValueOfSinglePic( png )
                self.videoFramesNpy[video].append( videoNpy )
                os.unlink( png )

    def RecognizeVideoDir( self, path ):
        pass
         
         

    def ChooseWhatToDo( self ):
        if (self.operate == 'get-id-dir') and (self.platform=='facer'):
            if not os.path.exists( self.hasTextDir ):
                os.makedirs( self.hasTextDir )
            if not os.path.exists( self.noTextDir ):
                os.makedirs( self.noTextDir )
            self.GetTextFromVideoDir( self.srcDir )
            ##self.SplitVideosToDir( )
            self.WriteUidToFile( )
        if (self.operate == 'get-id-file') and (self.platform=='facer'):
            self.hasTextDir = '\\'.join( self.srcDir.split('\\')[0:-1] ) + '\\has\\'
            self.noTextDir  = '\\'.join( self.srcDir.split('\\')[0:-1] ) + '\\no_has\\'
            if not os.path.exists( self.hasTextDir ):
                os.makedirs( self.hasTextDir)
            if not os.path.exists( self.noTextDir ):
                os.makedirs( self.noTextDir )
            self.GetTextFromVideo( self.srcDir )
            self.WriteResultToLog( self.srcDir )
            self.SplitVideosToDir( )
            self.CleanAllOfVideo( self.srcDir )
            self.WriteUidToFile( )
        if (self.operate=='search-id-file') and (self.platform=='facer'):
            self.SearchStringOnWebserverFromFile( self.srcDir )

        if (self.operate=='search-id-string') and (self.platform=='facer'):
            self.SearchStringOnWebserver( self.srcDir )

        if (self.operate=='face-id-file') and (self.platform=='facer'):
            if self.fm.IsMIMEType( self.srcDir, 'video' ):
                self.RecognizeSingleVideo( self.srcDir )
            else:
                print( '  <** Input file is not VIDEO FILE. - %s .> ' % self.srcDir )
                exit()
            
        if (self.operate=='face-id-dir') and (self.platform=='facer'):
            self.RecognizeVideoDir( self.srcDir )
        if (self.operate=='gen-npy') and (self.platform=='facer'):
            self.GenNpyFromDir( self.srcDir )

    def  Run( self ):
        self.ChooseWhatToDo( )
        

