#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import re
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
from filemanager.FileManager import FileManager

''' 自动上传到百度网盘, 自动寻找已经压缩好的目录，上传文件，./bdupload.py  path '''
## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')


class Uploader( object ):
    def __init__( self, srcDir, operate, platform ):
        self.srcDir     = srcDir
        self.operate    = operate
        self.platform   = platform
        self.needupFlag     = [ 'Concat_', 'concat_', 'Compress_', 'compress_', 'concat', 'Concat' ]

        self.fm = FileManager(
            srcDir          = self.srcDir,
            dstDir          = '',
            operate         = '',
            platform        = '',
            fileManagerData = '',
            password        = '' 
        )
        self.uploadQueue    = { }  ## filepath: networkpath
        self.logFile        = self.srcDir + 'uploader.log'

    ''' check this file need to upload or not? '''
    def IsNeedUp( self, path ):
        for flag in self.needupFlag:
            if flag in path:
                return True
        return False

    ''' get upload Dir queue. '''
    def GetUploadQueue( self, path ):
        self.fm.GetAllFiles( path, recursion=True )
        print( '  <** Upload - Under: %s .>' % path )
        for _dir in self.fm.allDirs:
            netdir = _dir.replace( path, '' )
            if netdir[-1] == '\\':
                netdir =  netdir[0:-1] 
            netdir = netdir.replace('\\', '/')
            print( '  <** - Create Net Dir: %s .>' % netdir )
            self.NetDiskMkdir( netdir ) 

        for _file in self.fm.allFiles:
            if self.fm.IsMIMEType( _file, 'video' ) and \
               self.IsNeedUp( _file ):
                netfile = _file.replace( path, '' ).replace( '\\', '/' )
                self.uploadQueue[ _file ] = netfile


    ''' mkdir on netdisk. '''
    def NetDiskMkdir( self, path ):
        cmd = 'bypy -q mkdir %s' % path
        try:
            pass
            ##os.system( cmd )
        except:
            pass
            ##os.system( cmd )


    ''' delete file on netdisk.'''
    def NetDiskDel( self, path ):
        pass

    ''' upload file from upload queue. '''    
    def  UploadFileFromQueue( self, queue={} ):
        tasknum = 0
        for _file in queue.keys( ):
            prefix = '%04d' % tasknum
            print( '  <** - Uploader - file: %s \t %s .>' % (_file, queue[_file]) )
            timeBefore = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logString  = '%s: %s Uploader: %s  -> %s\n' % (prefix, timeBefore, _file, queue[_file])
            self.fm.Writer( logString, self.logFile, 'a+' )
            self.UploadFile( _file, log=False )
            timeAfter = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logString  = '%s: %s Uploader Finish.\n' % (prefix, timeAfter)
            self.fm.Writer( logString, self.logFile, 'a+' )
            tasknum  = tasknum + 1


    ''' upload a dir to  netdisk. '''
    def UploadDir( self, path ):
        print('Upload-dir: ')
        self.GetUploadQueue( path )
        self.UploadFileFromQueue( self.uploadQueue )

    ''' upload a file to  network. '''
    def UploadFile( self, path, log=False ):
        netfile = ''
        prefix = '----'
        if log == True:
            print( 'Upload-file: %s' % path )
            timeBefore = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            netfile = path.split('\\')[-1]
            logString  = '%s: %s Uploader: %s  -> %s\n' % (prefix, timeBefore, path, netfile )
            self.fm.Writer( logString, self.logFile, 'a+' )
            cmd = 'bypy -q upload  %s' % netfile 
        cmd = 'bypy -q upload  %s' % path 
        try:
            pass
            ##os.system( cmd )
        except:
            pass
            ##os.system( cmd )
        if log==True:
            timeAfter = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logString  = '%s: %s Uploader Finish.\n' % (prefix, timeAfter)
            self.fm.Writer( logString, self.logFile, 'a+' )

    ''' choose what  should to be done. '''
    def ChooseWhatToDo( self ):
        if ( self.operate=='up-dir' ) and ( self.platform=='uploader' ):
            self.UploadDir( self.srcDir )
        if ( self.operate=='up-file' ) and ( self.platform=='uploader' ):
            self.UploadFile( self.srcDir, log=True )

    def Run( self ):
        self.ChooseWhatToDo( )


