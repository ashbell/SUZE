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
import zipfile
import cv2
import face_recognition as FR
import numpy 
import copy



"""
from xpinyin import Pinyin
from moviepy.editor import  VideoFileClip
from moviepy.editor import *
from pymediainfo import MediaInfo
from pprint import pprint
"""

## os.getenv( 'TZ' )  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv( 'TZ' )

''' MP4文件从mts格式，采用h264压缩成新的MP4文件'''
class  Compressor( ):
    def __init__(self, path='', file_flag='' ):
        self.compress_pwd = 'mojun'
        self.mp4_files = []
        self.search_flag = file_flag
        self.common_list = []
        self.workPath = os.getcwd() + '\\'
        self.rar = self.workPath + 'WinRAR\\Rar.exe'
        self.USERIDFILE = './allinfo'
        self.known_face_dir = './known_face/'

        ''' 把拖动输入的路径变成相对路径，C:\\'''
        if len( sys.argv ) > 1:
            path = sys.argv[1].split( '/' )[2:]
            path[0] = ( path[0]+':' ).upper()
            PyPath = '\\'.join( path )
        else:
            print( 'Argv  Path  is need!' )
            exit(  )

        if os.path.isdir(PyPath) and PyPath[-1] != '\\':
            PyPath = PyPath + '\\'
        self.relative_path = PyPath
        

    def ListMp4Files( self, path='' ):
        files = os.listdir( path )

        for f in files:
            file_path = path + f
            if os.path.isdir( file_path ):
                file_path = file_path +'\\'
                self.ListMp4Files(  file_path  )
            if ( file_path[-4:] == '.mp4'):
                if  self.search_flag  == '':
                    ''' 默认不指定则查找所有的MP4文件'''
                    self.mp4_files.append( file_path )
                elif self.search_flag in file_path:
                    self.mp4_files.append( file_path )
                else:
                    pass
                    

    def GetMp4Files( self ):
        path = self.relative_path
        self.mp4_files = []
        self.ListMp4Files(path)

        for mp4 in self.mp4_files:
            print(mp4)

        return self.mp4_files
    
    
    ''' 判定一个文件是否属于指定的类型,用file命令来获取，mimetypes.guess_type()不严谨,只根据后缀名判断而已'''
    def IsMIMEType(self, file_path ='', file_type=''):
        file_type = file_type.lower()
        similar = [ [ ],
                    [ 'video', 'mp4', 'mov', 'avi', 'ts', 'mts' ],    
                    [ 'photo', 'image','pic', 'jpeg', 'png',  'jpg', 'bmp' ],
                    [ 'json', 'JSON' ]
                
                  ]
        length = len(similar)
        similar_idx = 0
        for num in range( 0, length ):
            if file_type in similar[num]:
                similar_idx = num
                break

        if os.path.exists( file_path ) and ( file_type != '' ):
            ''' 在Linux中，一定要处理 '-' 这个符号，用引号把路径包围起来'''
            file_path = '\'%s\'' % file_path
            cmd = 'file %s' % file_path
            try:
                '''  冒号之后的空格 不可少, 这里还需要再斟酌，获取的结果包含了文件后缀, 是否去掉文件名'''
                '''  不去掉文件名，会导致文件名里有video就误判成视频文件，比如video-3.txt'''
                '''  Fucking this method output decode, not utf-8, cause error'''
                ##out = subprocess.getstatusoutput( cmd )[1].lower( ).split( ': ' )[1]

                '''  用check_output代替，自己转码'''
                out = subprocess.check_output( cmd, text=False )
                out = out.decode('utf-8')
                out = 'UTF - ' + out
                out = out.strip('\n').lower().split( ': ')[1]
                print( '%s' % out.strip('\n') )
            except:
                ##print( 'IsMIMEType Failed, Try GBK decode: %s' % file_path )
                try:
                    out = subprocess.check_output( cmd, text=False )
                    out = out.decode('gbk')
                    out = 'GBK - ' + out
                    print( '%s' % out.strip('\n') )
                except:
                    print( 'IsMIMEType Failed. : %s' % file_path )
                    return False

            for e in similar[similar_idx]:
               if e in out:
                   return True
            return False
        else:
            print( 'Input Para Error :%s : %s' %(file_path, file_type) )
            return False

    ''' 对MP4文件编码压缩'''
    def CompressMPEG4( self, file_path=''):
        dir_path  = '\\'.join(file_path.split('\\')[0:-1]) + '\\'
        file_name = file_path.split('\\')[-1:][0][0:-4]
        out_file = dir_path + file_name +'_'+'compressed_'  + str( random.randint(1000,9999 )) + '.mp4'
    
        cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -c:v libx264 -acodec  copy  -crf 20 -preset:v veryslow %s' \
                    % ( file_path, out_file )
        ##os.system( cmd )
        ##print(cmd)
        """
        subprocess.Popen(['C:\\cygwin64\\bin\\mintty.exe', '-e', 'ffmpeg','-hide_banner', '-v', 'quiet', '-stats', '-i', file_path, '-c:v', 'libx264',\
                '-acodec','copy', '-crf', '20', '-preset:v', 'veryslow', out_file ] )
        """

        if self.IsMIMEType(out_file, 'video'):
            return out_file
        else:
            return 'COMPRESS_FAIL'
    
    def GetFileList( self, path='', includedir='' ):
        lst = os.listdir(path)
        for f in lst:
            file_path = path  + f
            if os.path.isdir( file_path ):
                file_path = file_path + '\\'
                
                if includedir == True:
                    self.common_list.append( file_path )
                else:
                    pass
                self.GetFileList( file_path, includedir )
            elif os.path.isfile( file_path ):
                self.common_list.append( file_path )
            else:
                pass


    ''' 获取指定目录下的所有文件，includedir 指定返回的列表中是否包含文件夹, 否则只返回文件路径'''
    def GetAllFiles( self, path, includedir='' ):
        self.common_list = []
        if includedir==True:
            self.GetFileList( path, includedir=True )
        else:
            self.GetFileList( path, includedir=False )

        return self.common_list

    ''' 获取指定目录下，指定类型的文件，可递归可不递归, once找到一个就行了''' 
    def GetFilesWithType( self, path='', file_type = '', recursion=False, once=True  ):
        result = []
        if os.path.exists( path ) and os.path.isdir( path ):
            if recursion:
                files = self.GetAllFiles( path, includedir=False ) 
                for f in files:
                    if self.IsMIMEType( f, file_type ):
                        result.append( f )
                        if once:
                            break
                return result
            else:
                files = os.listdir( path )
                for f in files:
                    file_path = path + f
                    if os.path.isfile( file_path ) and \
                        os.path.exists( file_path ) and \
                        self.IsMIMEType( file_path, file_type ) :
                        result.append( file_path ) 
                        if once:
                            break
                return result
        else:
            print( 'GetFilesWithType: Input Para Error: \
                   path=%s | file_type=%s | recursion=%s ' %(path, file_type, recursion)
                 )
            result = []
            return result

    ''' 获取指定目录的大小，返回以Bytes为单位的大小'''
    def GetPathSize( self, path ):
        ''' return unit is Bytes, '''
        total_size = 0
        if os.path.isfile( path ):
            return os.stat(path).st_size

        if os.path.isdir( path ) :
            lst = self.GetAllFiles( path, includedir=False )
            for f in lst:
                f_size = os.stat(f).st_size
                total_size = total_size + f_size

            return total_size

    ''' 判断子父目录之间的关系, 找出父目录 '''
    def FindParentDir( self, path_lst=[] ):
        parent_dir = []
        copy_lst   = []
        ''' 深拷贝'''
        for f in path_lst:
            copy_lst.append(f)

        lenght = len(path_lst)
        for f in path_lst:
            num = 0
            sub = 0
            while( num < lenght ):
                if f in copy_lst[num]:
                    sub = sub + 1
                num = num + 1 
            ##print('sub --%d' % sub)
            if sub > 1:
                parent_dir.append(f)
        return parent_dir
        

    ''' 获取指定目录下所有子目录的大小,可用于查找没有内容的垃圾文件夹'''
    ''' path: 指定的目录， size: +10大于, -小于, 无符号表示等于, G=1024*1024*1024, M=1024*1024, k=1024,'''
    ''' +10k, 查找大于10k的，-10k查找小于10k'''
    ''' search_type: DIR: 只查找文件夹，FILE，只查找文件，None: 查找文件夹和文件'''
    def GetSpecifiedFiles( self, path='', size='', search_type='' ):
        unit = {'G':1024*1024*1024, 'g':1024*1024*1024, 'M':1024*1024, 'm':1024*1024, 'K':1024, 'k':1024 }
        per_unit = ''
        cmp      = ''
        num_size = ''
        dirlst   = []
        filelst  = []
        out      = []

        if len(size) > 2:
            size_unit = size[-1] 
            per_unit  = unit[size_unit]
            cmp       = size[0]
            num_size  = size[1:-1] 
        ''' 统一度量单位，转换成字节'''
        search_size = int(num_size) * per_unit

        lst = self.GetAllFiles( path, includedir=True )
        for f in lst:
            if os.path.isdir(f) and os.path.exists(f):
                dirlst.append(f) 
            if os.path.isfile(f) and os.path.exists(f):
                filelst.append(f)
        for f in dirlst:
            print(f)


        parent_dirs = self.FindParentDir( dirlst )
        ''' 有BUG，不完善, 问题多 '''

        if search_type == 'DIR':
            for f in parent_dirs:
                dir_size = self.GetPathSize(f)
                if cmp == '+':
                    if dir_size > search_size:
                        print('%s ->%s Mb'%(f, dir_size/(1024*1024)))
                if cmp == '-':
                    if dir_size < search_size:
                        print('DELETE - %s ->%s Mb'%(f, dir_size/(1024*1024)))
                        shutil.rmtree(f)
        if search_type == 'FILE':
            for f in filelst:
                print(f)


                
    def ZipCompressMP4( self, path='', havepwd='' ):
        if os.path.isdir( path ):
            if path[-1] != '\\':
                path = path + '\\'

            file_dir    = '\\'.join( path.split('\\')[0:-1]) + '\\'
            file_name   = path.split('\\')[-2:][0]
            zip_name    = file_name + '.zip'
            zip_file    = file_dir + zip_name
            if havepwd:
                zip_file = file_dir + 'PWD_' + zip_name
            if os.path.exists( zip_file ):
                zip_file = file_dir + 'Exists_' + zip_name

            if havepwd:
                cmd = '%s a -r -ep1 -p%s %s %s' % (self.rar, self.compress_pwd, zip_file, self.relative_path)
            else:
                cmd = '%s a -r -ep1  %s %s' % (self.rar, zip_file, self.relative_path)

            os.system(cmd)
        else: 
            file_dir    = '\\'.join( path.split('\\')[0:-1] ) + '\\'
            file_name   = path.split('\\')[-1:][0]  
            lst         = list(file_name)
            lst[-4:]    = '.zip'
            zip_name    = ''.join( lst )
            zip_file    = file_dir  +  zip_name 
            if havepwd:
                zip_file = file_dir + 'PWD_' + zip_name
                print(zip_file)
            if os.path.exists( zip_file ):
                zip_file = file_dir + 'Exists_' + zip_name

            if havepwd:
                cmd = '%s a -ep -p%s %s %s' % (self.rar, self.compress_pwd, zip_file, self.relative_path)
            else:
                cmd = '%s a -ep  %s %s' % (self.rar, zip_file, self.relative_path)
            os.system(cmd)

            """
                zipfile.ZipFile(file, mode='r', compression=ZIP_STORED, allowZip64=True, compresslevel=None)
                ZipFile.write(filename, arcname=None, compress_type=None, compresslevel=None)
          
            if havepwd:
                print('Use default password to create zip file.')
                z = zipfile.ZipFile( zip_file, 'w', zipfile.ZIP_DEFLATED, -9 )
                z.setpassword( self.compress_pwd.encode('utf-8') )
                saved_name = file_name
                z.write( path, arcname=saved_name, )
            else:
                z = zipfile.ZipFile( zip_file, 'w', zipfile.ZIP_DEFLATED )
            """

    ''' 给定 E:\CC\my\a.mp4, 将其MP4命名为 my_00.mp4的形式(author) '''
    ''' path: 指定的目录 '''
    ''' file_type: 指定要命名的文件类型, recursion: 是否递归, 不递归只命名根目录，递归 '''
    ''' 则把根目录连同子文件夹下的指定类型文件全部重新命名, 文件按照父目录的文件名字命名 '''
    def RenameFileAsRootDirName( self, path = '', file_type='', recursion_sub=False ):
        files = []
        if recursion_sub:
            files = self.GetFilesWithType( path, file_type, recursion=True, once=False )
        else: 
            files = self.GetFilesWithType( path, file_type, recursion=False, once=False )
        print('*')

        files_info = {}
        for f in files:
            root_dir = '\\'.join( f.split('\\')[0:-1] ) + '\\'
            file_name = f.split('\\')[-1:][0]
            if root_dir in files_info.keys():
                files_info[root_dir].append(file_name)
            else:
                files_info[root_dir] = [file_name]

        for root_dir in files_info.keys():
            print(root_dir)
            n = 1
            author = ''.join(root_dir.split('\\')[-2:])
            for f in files_info[root_dir]:
                sufix = '.' + f.split('.')[-1:][0]
                src_path = root_dir + f 
                name = '_%03d' % n
                new_name = author + name + sufix
                dst_path = root_dir +  new_name
                print( '\t%s --> %s'% (src_path, dst_path) )
                n = n +1

                if not os.path.exists(dst_path):
                    shutil.move(src_path, dst_path)
                else:
                    print( '\t  Dst exists: %s,  use  random file name' % dst_path )
                    new_name = author + name +'_e'+str(random.randint(10,99))+ sufix
                    dst_path = root_dir +  new_name
                    shutil.move(src_path, dst_path)


    ''' 指定path目录下，获取json文件，从中提取name字段，作者名字，写入allinfo文件中'''
    ''' 因为很多用户是没有关注的，通过网路没有获取到，但是ID是用视屏中提取的，也需要加到数据里'''
    ''' 保证在整理下载文件的时候，才能找到用户的ID'''
    ''' 返回： 3x6kaz5qvmbxb59 ---- 莫44975 '''
    def GetAuthorInfoFromJson( self, include_uid_path='' ):
        alpha       = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
                        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        digit       = ['0','1','2','3','4','5','6','7','8','9']
        result      = ''
        uid         = ''
        author      = ''
        files = p.GetFilesWithType( path=include_uid_path, file_type='json', recursion=True, once=True )
        if  os.path.exists( self.USERIDFILE ):
            fw = open( self.USERIDFILE, 'a+', encoding='utf-8' )
        else:
            fw = open( slef.USERIDFILE, 'w',  encoding='utf-8' )

        for f in files:
            print(f)
            fd = open( f, 'r', encoding='utf-8')
            lines = fd.readlines()
            fd.close()
            for line in lines:
                lst = line.split(',')
            for e in lst:
                if '"name":' in e:
                    try:
                        author = e.replace('"','').split(':')[1]
                    except:
                        print( '\t GetAuthorInfoFromJson: Failed: %s: %s' %(f, e) )
                        author = 'UNKONW'
                    break
            ''' 从路径中获取UID'''
            lst = f.split('\\')
            for e in lst:
                if '3x' in e:
                    uid_clst = []
                    e_lst = list(e)
                    for c in e_lst:
                        if ( c in alpha ) or ( c in digit ):
                            uid_clst.append(c)
                        else:
                            break
                    uid = ''.join( uid_clst )
            result = '%s ----  %s' % ( uid, author )
            fw.write( result )
            fw.write( '\n')
            print( result)
        fw.close()


    """ 指定目录下，对视频抽帧，对每个视频抽帧，返回一个字典，MP4: [PIC1, PIC2] '''
        path: 视频路径 
        count: 抽几次
        返回: { mp41:[pic1,pic2], mp42:[pic1, pic2] }
    """
    def GetFramesOfVideo( self, path='', count='' ):
        result = { }

        files = self.GetFilesWithType( path=path, file_type='video', recursion=True, once=False )
        for f in files:
            start = 3
            for cnt in range( 0, int(count) ):
                tmp   = f  + '_' + str(cnt) + '.png' 
                end   = start + 1
                cmd   = 'ffmpeg -nostats -loglevel 0  -y -ss %f -to %f -i %s -f image2 -vf   fps=fps=1/1 -qscale:v 2 %s' \
                        %(start, end, f, tmp)
                print( '%s\r' % tmp, end='' )
                if not os.path.exists( tmp ):
                    os.system( cmd )
                start = start + 1
                if os.path.exists( tmp ):
                    if f in result.keys():
                        result[f].append( tmp )
                    else:
                        result[f] = [ tmp ]
                else:
                    print( 'GetFrames Failed: %s : %s ' % (f, tmp) )

        return result

    ''' 对给定path的路径的图片做扫描，存储该图片的特征向量值，,128个特征值'''
    ''' 并返回特征向量文件的路径'''
    def GetEigenValueOfPicture( self, path='' ):
        npydata = ''
        npyfile = path + '_FR.npy'

        img_load = FR.load_image_file( path ) 
        try:
            npydata  = FR.face_encodings( img_load )[0] #获得128维特征值
            numpy.savetxt( npyfile, npydata )
        except:
            print('Failed to calc EigenValue: %s' % path)
            npyfile = ''

        return npyfile

    ''' 比较两张图片的特征值, 判断是否是同一个人, src, dst 图片路径''' 
    def CompareEigenValue( self, src='', dst='' ):
        known       = []
        if  src[-4:] == '.npy':
            srcnpy_file = src
        else:
            srcnpy_file =  src + '_FR.npy'
        if dst[-4:] =='.npy':
            dstnpy_file = dst
        else:
            dstnpy_file =  dst + '_FR.npy'

        if os.path.exists( srcnpy_file ):
            srcdata = numpy.loadtxt( srcnpy_file )
        else:
            src_load = FR.load_image_file( src )
            srcdata = FR.face_encodings( src_load )[0]
            numpy.savetxt( srcnpy_file, srcdata )

        if os.path.exists( dstnpy_file ):
            dstdata = numpy.loadtxt( dstnpy_file )
        else:
            dst_load = FR.load_image_file( dst )
            dstdata = FR.face_encodings( dst_load )[0]
            numpy.savetxt( dstnpy_file, dstdata )
        
        known.append( srcdata )

        ''' para 1 must be list'''
        ##matches = FR.compare_faces( known, dstdata, tolerance=0.55 )
        matches = FR.compare_faces( known, dstdata, tolerance=0.4 )
        return matches[0]


    ''' Loger记录器, logfile: 要保存的文件， loginfo: 信息, loglevel: log等级'''
    ''' Error: 0 | Warning: 1 | Info: 2 | '''
    def Loger( self, logfile='', loginfo='', loglevel='' ):
        if os.path.exists( logfile ):
            fd = open( logfile, 'a+', encoding='utf-8' )
        else:
            fd = open( logfile, 'w+', encoding='utf-8' )

        if loglevel == '0':
            print('Error - ')
        if loglevel == '2':
            fd.write(loginfo) 
            fd.write('\n')
        fd.close() 

    ''' 删除指定目录下的空文件夹，临时png文件'''
    def CleanDir( self, path='' ):
        dels = os.listdir( path )
        for f in dels:
            file_path = path + f
            if '.png' == file_path[-4:]:
                os.remove( file_path )
            if ( os.path.isdir(file_path) ) and \
                    ( len(os.listdir(file_path)) == 0 ):
                shutil.rmtree( file_path )


    ''' 对path目录下所有的视频抽帧，并计算出每帧图片的特征向量,注意处理横屏时候的图像 '''
    ''' 人脸必须是竖屏，否则无法正常计算特征向量'''
    ''' path: video目录, framecnt: 每个视频抽几帧,  '''
    ''' record: 读取历史记录，直接npy文件路径比较'''
    def GetFramesOfAllVideos( self, path='', framecnt=0, record=''):
        video_npy   = {}
        npys        = []
        cmp         = ''
        if record and os.path.exists( record ):
            print('****** Use Record File:\n')
            fd      = open( record, 'r', encoding='utf-8' )
            lines   = fd.readlines()
            fd.close()
            for f in lines:
                npys.append( f.strip('\n') )
        else:
            video_frames = self.GetFramesOfVideo( path=path, count=int(framecnt) )
            for video in video_frames.keys():
                frames = video_frames[video]   
                for frame in frames:
                    print( 'GetEigenValue: %s\r' % frame, end='' )
                    npy = self.GetEigenValueOfPicture( frame )
                    if (video in video_npy.keys()):
                        if npy:
                            video_npy[video].append( npy )
                    else:
                        if npy:
                            video_npy[video]  =  [npy]
            print( '*'*100 )
            for video in video_npy:
                print( '%s'% video, end='')
                for npyfile in video_npy[video]:
                    print( '\t%s' % npyfile, end='' )
                    npys.append( npyfile )
                    self.Loger( './LOG',npyfile, '2'  )

        npysa = npys 
        npysb = copy.deepcopy( npys ) 
        for npya in npysa:
            bdel = []
            src_file_name   = npya.split('\\')[-1].split('_')[0]
            src_file_dir    = '\\'.join( npya.split('\\')[0:-1] ) + '\\'
            src_file        = src_file_dir  +  src_file_name
            mp4_dir         = src_file_dir + src_file_name.split('.')[0] + '\\'
            new_src_file    = mp4_dir +  src_file_name

            for  npyb in npysb:
                dst_file_name   = npyb.split('\\')[-1].split('_')[0]
                dst_file_dir    = '\\'.join( npyb.split('\\')[0:-1] ) + '\\'
                dst_file        = dst_file_dir  +  dst_file_name
                new_dst_file    = mp4_dir  + dst_file_name
                cmp = False
                if (src_file == dst_file):
                    pass
                else:
                    cmp = self.CompareEigenValue( npya, npyb )
                if cmp == True:
                    if not os.path.exists( mp4_dir ):
                        os.makedirs( mp4_dir )
                    if os.path.exists( src_file ):
                        shutil.move( src_file, new_src_file )
                   
                    info = '%s=%s' % (src_file, dst_file )
                    if src_file != dst_file:
                        print( '%s == %s' %(src_file, dst_file), end='' )
                    self.Loger( './EQUA', info, '2' )
                    bdel.append( npyb )
                    if os.path.exists( dst_file ):
                        shutil.move( dst_file, new_dst_file )
                else:
                    ''' No Find Same Person'''
                    pass
                    
            for delete in bdel:
                npysb.remove( delete )

        ''' 清理下战场'''
        self.CleanDir( path=src_file_dir + '\\' )

    ''' 对指定目录下的MP4文件，生成对应的srt字幕文件，给工具使用'''
    def GenSrtInPath( self, path='', recursion=True, once=False ):
        files = self.GetFilesWithType( path=path, file_type='video', recursion=recursion, once=once )
        for f in files:
            pos = [i for i in range(len(f)) if f[i]=='.']
            dim = pos[-1]
            prev = f[ 0 : dim ]
            srt  = prev+'.srt'
            if os.path.exists( srt ):
                pass
            else:
                print( 'GenSrt - %s' % srt )
                fd = open( srt, 'w+', encoding='utf-8' )
                fd.write( 'Subedit 1\n')
                fd.write( 'Subedit 2\n')
                fd.write( 'Subedit 3\n')
                fd.close()


      
          


p = Compressor('CCCC', '')
p.GenSrtInPath( path=p.relative_path, recursion=True, once=False)
##p.GetFramesOfAllVideos(p.relative_path, framecnt=3, record=r'C:\Users\Administrator\Desktop\LOG')
##p.RenameFileAsRootDirName( path=p.relative_path, file_type='video', recursion_sub=True)
##cc = p.GetFilesWithType( path=p.relative_path, file_type='json', recursion=True, once=True)
##p.GetAuthorNameFromJson( path=p.relative_path)
#p.GetAuthorInfoFromJson( include_uid_path=p.relative_path)
##CC= p.GetFramesOfVideo( path=p.relative_path, count= 2 )
print('-'*100)
##p.CompareEigenValue(r'C:\Users\Administrator\Desktop\TEST\002.jpg', r'C:\Users\Administrator\Desktop\TEST\009.jpg')

##p.GetSpecifiedFiles( p.relative_path, size='-20M', search_type='DIR')
##p.CompressMPEG4(p.GetMp4Files()[0])
##p.ZipCompressMP4(p.relative_path, havepwd=True)
##CC= p.GetAllFiles('C:\\BaiduNetdiskDownload\\', includedir=True)
##dd= p.GetPathSize('C:\\BaiduNetdiskDownload\\')


"""
ProgressBar Or You can also use the carriage return:
    sys.stdout.write("Download progress: %d%%   \r" % (progress) )
    sys.stdout.flush()

def IsWantToFind( mp4_path='', flag='' ):
    mp4_root_dir = '\\'.join( mp4_path.split('\\' )[0:-2]) + '\\'
    lst = os.listdir( mp4_root_dir )
    result = False
    for f in lst:
        if flag in f:
            result = True
    return result


def FindWantDir( flag='' ):
    WannaDir = []
    GetMp4Dir( SrcDir )
    for path in Mp4Dir:
        if IsWantToFind( path, flag ):
            mp4_root_dir = '\\'.join( path.split('\\' )[0:-2]) + '\\'
            WannaDir.append( mp4_root_dir )
            ##print( '%s ----> %s' %(mp4_root_dir, flag ))
    
    return WannaDir

def IsMp4File( path ):
    if os.path.isfile( path ):
        return ( path.split('.' )[-1] == 'mp4')
    return False

    

def CompressMPEG4( dir_path ):
    logfile = './compresslog'
    if os.path.exists( logfile ):
        fd = open( logfile, 'a+', encoding='utf-8' )
    else:
        fd = open( logfile, 'w+', encoding='utf-8' )
    lst = os.listdir( dir_path )
    for f in lst:
        file_path = dir_path + f
        if ( 'concat_' in f ) and (IsMp4File(file_path)):
            OutFile = dir_path + 'compressed_'  + str( random.randint(1000,9999 )) + '.mp4'
            ''' Fuck chinese  align'''
            loginfo = '[ Convert - %s\t\t - %s ]' % ( file_path,OutFile ) 
            print( loginfo )
            cmd = 'ffmpeg -hide_banner -v quiet -stats -i %s -c:v libx264 -acodec  copy  -crf 20 -preset:v veryslow %s' \
                    % ( file_path, OutFile )
            os.system( cmd )

            fd.write( loginfo + '\n' )
            print( '[ Delete - %s ]' % (file_path ) )
            os.unlink( file_path )
            ##input( '>>' )
    fd.close(  )        

        
Dirs = FindWantDir( 'concat_' )
for path in Dirs:
    CompressMPEG4( path )

"""
