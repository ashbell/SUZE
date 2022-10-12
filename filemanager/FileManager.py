#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import time
import wget
import codecs
import datetime
import random
import threading
import requests
import base64
import subprocess
import urllib.request
import shutil
import numpy as np
import hashlib
from urllib.parse import unquote
from threading    import Thread, Lock
from xpinyin      import Pinyin


class FileManager( object ):
    def __init__( self, srcDir, dstDir, operate, platform, fileManagerData, password ):
        print( '< ** Init FileManger................>')
        self.myKsUid = '3xnzffmzps58emw'
        self.cwd = os.getcwd() + '\\'
        self.workPath = self.cwd
        self.dataBaseDir= self.cwd + 'database\\'
        ##self.ksFeedInfoFile = self.dataBaseDir + self.myKsUid + '.feeds'
        self.ksAllFeedsInfoFile = self.dataBaseDir + 'allinfo'
        self.ksAllFeedsUidName = { }
        self.uidNameDir = { }   ## 3xxadad: W我的小可爱  dir
        self.jsonFilesNick = { } ## 001.json:  nickname
        self.srcDir = srcDir
        self.dstDir = dstDir
        self.operate = operate
        self.platform = platform
        self.inputPath = ''
        self.recursion = True
        self.wannaOperateDirs = [ ]
        self.allDirs = [ ]

        self.alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
                      'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        self.digit = ['0','1','2','3','4','5','6','7','8','9']

        self.fileManagerData = fileManagerData
        ##print('----->>', self.fileManagerData)
        self.sameFileTypes = [ [ ],
                    [ 'video', 'mp4', 'mov', 'avi', 'ts', 'mts', 'flv' ],    
                    [ 'photo', 'image','pic', 'jpeg', 'png',  'jpg', 'bmp' ],
                    [ 'json', 'JSON', 'utf-8 unicode text' ],
                    [ 'mp3', 'audio' ]
                
                  ]
        self.allFiles = [ ]   ## files only
        self.allDirs  = [ ]   ## dirs  only
        self.allPaths = [ ]   ## files + dirs 
        self.result   = [ ]
        self.sizeUit  = { 'G':1024*1024*1024, 'g':1024*1024*1024, 'M':1024*1024, 'm':1024*1024, 'K':1024, 'k':1024 }
        self.pathSize = { }

        self.jsonFileStrings = { }  ## file: [it's lines]
        self.jsonFileStringsSlice = { }  ## file: [string split ',' ]
        self.jsonFilesNick = { }  ## file.json : nick
        self.uniqueFiles = [ ]
        self.repeatFiles = [ ]

        self.zipToolPath = self.workPath + 'bin\\WinRAR\\Rar.exe'
        self.videoFilesPath  = [ ]
        self.zipDefaultPassword = password

    ''' write string data to file '''
    def Writer( self, data, wfile, mode='' ):
        if mode == 'wb':
            with open( wfile, mode ) as f:
                f.write( data )
        else:
            with open( wfile, mode, encoding='utf-8' ) as f:
                f.write( data )

    ''' read file, return lines[]'''
    def Reader( self, rfile ):
        lines = []
        with open( rfile, 'r', encoding='utf-8' ) as f:
            lines = f.readlines()
        return lines
    
    ''' move downloaded  ks dir-files to dst. '''
    ''' 3xaaaaa/111.mp4, get uid-name, use first alpha of chinese name as root dir'''
    ''' get all uid-legal-name from database file'''
    def GetAllUidName( self ):
        lines = self.Reader( self.ksAllFeedsInfoFile )
        for line in lines:
            listCharOfName = []
            line = line.strip( '\n' )
            if len(line) > 0:
                lst = line.split('----') 
                names = lst[1].replace( ' ', '' )
                uid = lst[0].replace( ' ', '' )
            allNames = names.split( '--' )
            originName = allNames[0]
            namelen = len( originName )
            namelst = list( originName )
            for char in namelst:
                if ( '\u4e00' <= char <= '\u9fff' ):
                    listCharOfName.append( char )
                if char in self.alpha:
                    listCharOfName.append( char )
                if char in self.digit:
                    listCharOfName.append( char )
            legalName = ''.join( listCharOfName )
            self.ksAllFeedsUidName[uid] = legalName

    ''' get fir upper alpah of chinese/english name.'''
    def GetFirstAlphaOfName( self ):
        pinyin = Pinyin( )
        for uid in self.ksAllFeedsUidName.keys():
            legalName = self.ksAllFeedsUidName[uid]
            firstAlpha = pinyin.get_pinyin( legalName )[0].upper()
            nameDir = firstAlpha + legalName
            self.uidNameDir[uid] = nameDir

    ''' get  all dirs of src dir '''
    def GetAllDirsOfSrcDir( self, src ):
        ##print('++++' +src)
        lst = os.listdir( src )
        for f in lst: 
            path = src + f
            if os.path.isdir( path ):
                path = path + '\\'
                if self.recursion == True:
                    self.GetAllDirsOfSrcDir( path )
                self.allDirs.append( path )

    ''' filter wanna dirs from all dirs.'''
    def FilterWannaDirsFromAllDirs( self ):
        for path in self.allDirs:
            if '3x' in path:
                self.wannaOperateDirs.append( path )

    ''' clean/arrange dst dir, del json, make class A/B/C/D dir'''
    def ArrangeDstDir( self, dstPath ):
        lst = os.listdir( dstPath )
        for f in lst:
            path = dstPath + f 
            if ( os.path.isfile(path) ) and ( '.json' in path ):
                os.unlink( path )
            if ( os.path.isdir(path) )  and ( 'video' in path ):
                path = path + '\\'
                os.makedirs( path + 'A\\' )
                os.makedirs( path + 'B\\' )
                os.makedirs( path + 'C\\' )
                os.makedirs( path + 'D\\' )

    ''' move wanna dirs to dst dir(in subdir) '''
    def MoveWannaDirsToDstDir( self ):
        for src in self.wannaOperateDirs:
            srcUid = src.split('\\')[-2]
            if ( srcUid in self.uidNameDir.keys() ):
                dstDirName = self.uidNameDir[srcUid]
                dstPath = self.dstDir + dstDirName + '\\'
                if ( not os.path.exists(dstPath) ):
                    print( '  <Move - %s    -->  %s' %( src, dstPath) )
                    shutil.move( src, dstPath )
                    self.ArrangeDstDir( dstPath )
                    dstUidFile = dstPath + srcUid + '.txt'
                    self.Writer( srcUid, dstUidFile, 'w' ) 
                else:
                    print( '  <dst - %s    exits!' %(dstPath) )
            else:
                print('not in database: %s' % srcUid)

    ''' rename specified type files as parent-dir name. '''
    ''' check path file is belong to filetype or not.'''
    def IsMIMEType( self, path, fileType ):
        fileType = fileType.lower( )
        length = len( self.sameFileTypes )
        similar_idx = 0
        for num in range( 0, length ):
            if fileType in self.sameFileTypes[num]:
                similar_idx = num
                break

        ''' 在Linux中，一定要处理 '-' 这个符号，用引号把路径包围起来'''
        path = '\'%s\'' % path
        cmd = 'file --mime-type %s' % path
        try:
            '''  用check_output代替，自己转码'''
            out = subprocess.check_output( cmd, text=False )
            out = out.decode('utf-8')
            out = 'UTF - ' + out
            out = out.strip('\n').lower().split( ': ')[1]
            ##print( '%-80s    -  %s' % (path,out.strip('\n')) )
        except:
            ##print( 'IsMIMEType Failed, Try GBK decode: %s' % path )
            try:
                out = subprocess.check_output( cmd, text=False )
                out = out.decode('gbk')
                out = 'GBK - ' + out
                ##print( '%s' % out.strip('\n') )
            except:
                print( 'IsMIMEType Failed. : %s' % path )
                return False
                
        for e in self.sameFileTypes[similar_idx]:
            if e in out:
                return True
        return False

    ''' get all files of dir. save result in self.allFiles[]'''
    def GetAllFiles( self, path, recursion ):
        lst = os.listdir( path )
        for f in lst:
            filePath = path + f
            if recursion == False:
                if os.path.isfile( filePath ):
                    self.allFiles.append( filePath )
                if os.path.isdir( filePath ):
                    fielPath = filePath +  '\\'
                    self.allDirs.append( filePath )
                self.allPaths.append( filePath )
            elif recursion == True:
                if os.path.isdir( filePath ):
                    filePath = filePath + '\\'
                    self.allDirs.append( filePath )
                    self.allPaths.append( filePath )
                    self.GetAllFiles( filePath, True )
                if os.path.isfile( filePath ):
                    self.allFiles.append( filePath )
                    self.allPaths.append( filePath )
            else:
                pass

    ''' 获取指定目录下，指定类型的文件，可递归可不递归, once找到一个就行了'''
    def GetFilesWithType( self, path='', fileType='', recursion=False, once=False  ):
        self.allFiles = [ ]
        self.GetAllFiles( path, recursion=recursion )
        for f in self.allFiles:
            if self.IsMIMEType( f, fileType ):
                self.result.append( f )
                if once:
                    break

    ''' 获取指定目录的大小，返回以Bytes为单位的大小'''        
    def GetPathSize( self, path ):
        ''' return unit is Bytes, '''
        ##print('get path size: %s' % path)
        totalSize = 0
        if os.path.isfile( path ):
            sz = os.stat(path).st_size
            self.pathSize[path] = sz
            return sz

        if os.path.isdir( path ) :
            self.allPaths = []
            self.GetAllFiles( path, recursion=True )
            for f in self.allPaths:
                fsize = os.stat(f).st_size
                totalSize = totalSize + fsize
        self.pathSize[path] = totalSize
        return totalSize

    ''' 获取指定目录下所有子目录的大小,可用于查找没有内容的垃圾文件夹'''
    ''' path: 指定的目录， size: +10大于, @小于, 无符号表示等于, G=1024*1024*1024, M=1024*1024, k=1024,'''
    ''' +10k, 查找大于10k的，-10k查找小于10k'''
    ''' search_type: DIR: 只查找文件夹，FILE，只查找文件，None: 查找文件夹和文件'''
    def FindSpecifiedSizeFiles( self, path, size, searchType ):
        input('\t<Warning....Find dir size contain sub. need to continue? >:')
        searchSize = 0
        if len( size ) > 2:
            sizeUit     = size[-1]
            unitBytes   = self.sizeUit[sizeUit] ## convert unit to bytes
            relation    = size[0]
            numUnit     = size[1:-1] ## how many units it has.
            searchSize  = int(numUnit) * unitBytes
        if searchSize == 0:
            print('Error when convert size.')
            exit()
        self.allPaths = []
        self.allFiles = []
        self.allDirs  = []
        self.GetAllFiles( path, recursion=True )
        
        '''  A目录下有许多子目录组成，每个子目录不大于，加起来总的就大于，输出都是子目录'''
        '''  此时该如何判定？'''
        if ( searchType=='DIR' )  and ( relation=='+' ):
            for path in self.allDirs:
                pathSize = self.GetPathSize( path )
                if pathSize > searchSize:
                    self.result.append( path )
        if ( searchType=='DIR' ) and ( relation=='-' ):
            for path in self.allDirs:
                pathSize = self.GetPathSize( path )
                if pathSize < searchSize:
                    self.result.append( path )

        if ( searchType=='FILE' ) and ( relation== '+'):
            for path in self.allFiles:
                pathSize = self.GetPathSize( path )
                if pathSize > searchSize:
                    self.result.append( path )

        if ( searchType=='FILE' ) and ( relation=='-'):
            for path in self.allFiles:
                pathSize = self.GetPathSize( path )
                if pathSize < searchSize:
                    self.result.append( path )

        for v in self.result:
            mbUnitSize = round( self.pathSize[v]/(1024*1024),2 )
            out = ('%10s Mb - %s' % ( mbUnitSize, v) )
            print(out)
            if os.path.exists( v ):
                shutil.rmtree( v )

    ''' 给定 E:\CC\my\a.mp4, 将其MP4命名为 my_00.mp4的形式(author) '''
    ''' path: 指定的目录 '''
    ''' file_type: 指定要命名的文件类型, recursion: 是否递归, 不递归只命名根目录，递归 '''
    ''' 则把根目录连同子文件夹下的指定类型文件全部重新命名, 文件按照父目录的文件名字命名 '''
    def RenameFileAsRootDirName( self, path='', fileType='', recursionSub=False ):
        self.result = []
        if recursionSub == True:
            self.GetFilesWithType( path, fileType, recursion=True, once=False )
        elif recursionSub == False: 
            self.GetFilesWithType( path, fileType, recursion=False, once=False )
        else:
            print('Fuck you!!!!!!!!!!')

        dirWithFiles = { }
        for f in self.result:
            parentDir = '\\'.join( f.split('\\')[0:-1] ) + '\\'
            filename = f.split( '\\' )[-1:][0]
            if parentDir in dirWithFiles.keys():
                dirWithFiles[parentDir].append( filename )
            else:
                dirWithFiles[parentDir] = [ filename ]

        for parentDir in dirWithFiles.keys():
            fileCnt = 1
            author = ''.join( parentDir.split('\\' )[-2:])
            for f in dirWithFiles[ parentDir ]:
                sufix = '.' + f.split('.')[-1:][0]
                srcPath = parentDir + f 
                name = '_%03d' % fileCnt
                newname = author + name + sufix
                dstPath = parentDir +  newname
                fileCnt = fileCnt +1

                extraInfo = ''
                if  os.path.exists( dstPath ):
                    extraInfo = '  <DstExists!>'
                    ##print( '\t  Dst exists: %s,  use  random file name' % dstPath )
                    newname = author + name +'_e'+str(random.randint(10,99))+ sufix
                    ##newpath = parentDir + newname
                    ##print( '  <** - Reanme As tmp:%s .>' % newpath)
                    ##shutil.move( dstPath, newpath )
                    dstPath = parentDir +  newname
                print( '%s  %s --> %s'% (extraInfo, srcPath, dstPath) )
                shutil.move( srcPath, dstPath )
    
    ''' get all subdir of path, filter uid dir.'''
    def GetUidDirs( self, path ):
        uidDirs = [ ]
        self.allDirs = []
        self.GetAllFiles( path=path, recursion=True )
        for subDir in self.allDirs:
            uid = subDir.split('\\')[-2]
            if '3x' in uid :
                uidDirs.append( subDir )
        return uidDirs


    ''' 指定path目录下，获取json文件，从中提取name字段，作者名字，写入allinfo文件中'''
    ''' 因为很多用户是没有关注的，通过网路没有获取到，但是ID是用视屏中提取的，也需要加到数据里'''
    ''' 保证在整理下载文件的时候，才能找到用户的ID'''
    ''' 返回： 3x6kaz5qvmbxb59 ---- 莫44975 '''
    def GetAuthorInfoFromUidDir( self, pathUidIn ):
        self.result = []
        self.GetFilesWithType( path=pathUidIn, fileType='json', recursion=True, once=True )
  
        for jsfile in self.result:
            lines = self.Reader( jsfile )
            self.jsonFileStrings[ jsfile ] = lines

        for jsfile in self.jsonFileStrings.keys( ): 
            strings = self.jsonFileStrings[ jsfile ]
            stringsSlice = ''.join( strings ).split( ',' )
            self.jsonFileStringsSlice[ jsfile ] = stringsSlice

        for jsfile in self.jsonFileStringsSlice:
            words = self.jsonFileStringsSlice[ jsfile ]
            nickname = ''
            for word in words:
                if '"name":' in word:
                    nickname = word.replace('"','').split(':')[1]
                    break
            if nickname == '':
                print('  <E>Cannot get nick name from: %s.' % jsfile )
                nickname = 'unknow'+ str( random.randint(100,999) ) + '_' 

            self.jsonFilesNick[ jsfile ] = nickname
        

    ''' get AuthorInfo from path. search uid sub-dir, read json, parse/write nick name '''
    def GetAuthorInfoFromPath( self, path ):
        uidDirs = self.GetUidDirs( path )
        for uidDir in uidDirs:
            self.GetAuthorInfoFromUidDir( uidDir )

        ''' end loop, writer to database.'''
        for jsfile in self.jsonFilesNick.keys():
            uid = jsfile.split( '\\' )[-2]
            if '3x' in uid:
                string = '%s ----  %s\n' % ( uid, self.jsonFilesNick[ jsfile ] )
                self.Writer( string, self.ksAllFeedsInfoFile, 'a+' )
                print( 'Writer: - ', string.strip('\n'), '  ', jsfile )



    ''' give a file list, return unique files by md5 check.'''
    def GetUniqueFilesByHash( self, files ):
        mbBytes = 1024*1024
        hashes = [ ]
        for f in files:
            ''' Need to consider how many bytes to read is best.'''
            hashVal = hashlib.md5( open(f,'rb').read(mbBytes) ).hexdigest()
            hashes.append( hashVal )

        uniques = list( set(hashes) )
        npAllHashes = np.array( hashes )
        groups = [ ]
        for uq in uniques:
            sameIndex = np.where( npAllHashes == uq )[0]
            groups.append( sameIndex.tolist() )
        for item in groups:
            length = len( item )
            if length > 1:
                self.uniqueFiles.append( files[ item[0] ] )
                repeatIndex = item[1:]
                for num in repeatIndex:
                    self.repeatFiles.append( files[num] )
            else:
                self.uniqueFiles.append( files[ item[0] ] )

    
    ''' compare src to dst, find same/repeat file, then delete them.'''
    ''' if dst given, compare to, else find src same file to delete.'''
    def DeleteSameFiles( self, src, dst ):
        self.allFiles = [ ]
        self.GetAllFiles( src, recursion=True )
        if dst !='' :
            self.GetAllFiles( dst, recursion=True )
        self.pathSize = { }
        for file in self.allFiles:
            self.GetPathSize( file ) 
        sizes = [ ] 
        for v in self.pathSize.keys( ):
            sizes.append( self.pathSize[v] )

        uniqueSizes = list( set( sizes ) )
        allFiles = [ ]
        for file in self.pathSize.keys():
            allFiles.append( file )

        npAllSizes = np.array( sizes )
        groups = [ ] 
        sameSizeGroup = [ ]
        for uniqueSize in uniqueSizes:
            sameSizeIndex = np.where( npAllSizes == uniqueSize )[0]
            groups.append( sameSizeIndex.tolist() )

        for item in groups:
            if len( item ) > 1:
                sameSizeGroup = [ ]
                for pos in item:
                    sameSizeGroup.append( allFiles[ pos ] )
                self.GetUniqueFilesByHash( sameSizeGroup )  
            else: 
                self.uniqueFiles.append( allFiles[ item[0] ] )

    ''' delete repeat files.'''
    def DeleteRepeatFiles( self ):
        for rfile in self.repeatFiles:
            print('  <Delete Repeate File:>  %s .' % rfile )
            os.unlink( rfile )

    ''' generate srt file of videos. '''
    def GenerateSrtOfVideos( self ):
        self.result = [ ]
        self.videoFilesPath =  self.result
        self.GetFilesWithType( path=self.srcDir, fileType='video', recursion=False, once=False )
        for videoFile in self.videoFilesPath:
            slices = videoFile.split( '\\' )
            filename = '.'.join( slices[-1].split('.')[0:-1] )  ##filename.mp4  -> filename
            suffix = '.srt' 
            fileDir = '\\'.join( slices[0:-1] ) + '\\'
            srtFilePath = fileDir + filename + suffix
            if os.path.exists( srtFilePath ):
                srtFilePath = fileDir + filename + '_e_' + suffix
            strings = 'subedit 1\nsubedit 2\nsubedit 3\n'
            self.Writer( strings, srtFilePath, 'w+' )
            print( '  <* GenSrt - %s .>' %  srtFilePath )

    ''' zip single file. '''    
    def zipSingleFile( self, path, havepwd ):
        slices = path.split( '\\' )
        fileDir = '\\'.join( slices[0:-1] ) + '\\'
        filename = '.'.join( slices[-1].split('.')[0:-1] )
        zipFilePath = fileDir + filename + '.zip'
        
        if havepwd == True:
            cmd = '%s a -ep -p%s %s %s' %  \
                  ( self.zipToolPath, self.zipDefaultPassword, zipFilePath, path )
        if havepwd == False:
            cmd = '%s a -ep  %s %s' %  \
                  ( self.zipToolPath, zipFilePath, path )
        ##os.system( self.zipToolPath )
        os.system(cmd)


    ''' zip a dir. '''
    def zipDir( self, path, havepwd ):
        slices = path.split( '\\' )
        parentDir = '\\'.join( slices[0:-2] ) + '\\'
        dirname = slices[-2]
        zipPath = parentDir + dirname + '.zip'
        if os.path.exists( zipPath ):
            zipPath = parentDir + dirname + '_e_' + '.zip'

        if havepwd == True:
            cmd = '%s a -r -ep1 -p%s %s %s' % \
                  ( self.zipToolPath, self.zipDefaultPassword, zipPath, path )
        if havepwd == False:
            cmd = '%s a -r -ep1  %s %s' % \
                  ( self.zipToolPath, zipPath, path )
        os.system( cmd )


    ''' compress path given files to zip use winzip.'''
    def CompressFilesToZip( self, path, havepwd ):
        if os.path.isfile( path ):
            self.zipSingleFile( path, havepwd )
        if os.path.isdir( path ):
            self.zipDir( path, havepwd )
        """ 
        self.GetAllFiles( path=path, recursion=True )
        for v in self.allPaths:
            pass
        """
         

    ''' choose what should to be done.'''
    def ChooseOperateToDo( self ):
        if ( self.operate == 'find' ) and ( self.platform == 'filemanager' ):
            self.srcDir = self.fileManagerData[0]
            searchSize  = self.fileManagerData[1]
            fileType    = self.fileManagerData[2]
            self.GetPathSize( self.srcDir )
            self.FindSpecifiedSizeFiles( self.srcDir, searchSize, fileType )
        if ( self.operate=='rename-asauth' ) and ( self.platform=='filemanager'):
            self.srcDir = self.fileManagerData[0]
            fileType    = self.fileManagerData[1]
            recursion   = self.fileManagerData[2]
            self.RenameFileAsRootDirName( path=self.srcDir, fileType=fileType, recursionSub=recursion )

        if ( self.operate=='parse' ) and ( self.platform=='ks' ):
            self.GetAuthorInfoFromPath( self.srcDir )

        if ( self.operate=='del_same') and ( self.platform=='filemanager' ):
            self.DeleteSameFiles( self.srcDir, self.dstDir )
            self.DeleteRepeatFiles( )
        if ( self.operate=='gen-srt' ) and ( self.platform=='filemanager' ):
            self.GenerateSrtOfVideos( )

        if ( self.operate=='zip-files') and ( self.platform=='filemanager' ):
            if self.zipDefaultPassword == '':
                self. CompressFilesToZip( self.srcDir, False )
            else:
                self.CompressFilesToZip( self.srcDir, True )
        
            
    def Run( self ):
        self.ChooseOperateToDo( )
        ##self.GetPathSize( self.srcDir )
        ##self.FindSpecifiedSizeFiles( self.srcDir, '+10M', 'DIR' )
        """
        self.GetFilesWithType( self.srcDir, 'photo', True, True )
        print('****************withType************************')
        for v in self.result:
            print(v)
        """
        """
        self.GetAllUidName( )
        self.GetFirstAlphaOfName( )
        self.recursion = False
        self.GetAllDirsOfSrcDir( self.srcDir )
        self.FilterWannaDirsFromAllDirs( )
        self.MoveWannaDirsToDstDir( )
        self.GetAllFiles( self.srcDir, True )
        print('**************allFiles**********************')
        for v in self.allFiles:
            print(v)
        print('************all Dirs************************')
        for v in self.allDirs:
            print(v)
        print('************all paths************************')
        for v in self.allPaths:
            print(v)
        """




        
        

                    
            




