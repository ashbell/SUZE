#!/usr/bin/env  python
# -*- coding: utf-8 -*-

import os
import sys
import time
import threading
from time import ctime, sleep
import subprocess
import re

""" 搜索目录下所有的媒体文件，用ffmpeg转换成制定类型的
     ./convert.py  workdir
     ./convert.pt g:/FLVAA/N妮妮
"""
max_thread = 4
bash_path = "C:\\cygwin64\\bin\\mintty.exe"
ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
SRC_TYPE = 'flv'
DST_TYPE = 'mp4'

##work_dir = os.path.abspath( sys.argv[1] )
work_dir = sys.argv[1]
s1 = work_dir.replace( '/cygdrive/', '' )
work_dir = s1.replace( s1[0], s1[0]+':' )
print( "Get work_dir: %s" % work_dir )
file_lists = []


def get_file_lists( work_dir, file_type ):
    """获取目录下指定类型文件的完整路径
    """
    if work_dir[-1] != '/':
        work_dir = work_dir + '/'
    for lists in os.listdir( work_dir ):
        path = os.path.join( work_dir, lists )

        if file_type in path:
            dim = '\.'
            id = [ i.start() for i in re.finditer( dim, path) ]
            start = id [-1] + 1
            type_name = path[ start: ]
            type_name =type_name.lower()

            if type_name == file_type.lower():
                file_lists.append( path )

        if os.path.isdir( path ):
            get_file_lists( path, file_type )

def convert_to_dst_type( file, src_type, dst_type ):
    """ 把指定的文件file, 转换成目标类型
    """
    if os.path.isfile( file ) and os.path.exists( file ):
        dim = '/'
        id = [ i.start() for i in re.finditer( dim, file )]
        start = 0
        end = id[-1] + 1
        dst_dir = file[ start : end ]
        file_name = file[ end : ]
        file_name = file_name.split('.')[0] + '.' + dst_type.lower()
        dst_file_path =  dst_dir + file_name

        print("%-60s \t ==> %-60s" % (file, dst_file_path))

        ##  ffmpeg -i "$i" -ar 44100 -ac 2 -vcodec copy "$i".mp4; 
        p =  subprocess.Popen([bash_path, ffmpeg_path, "-hide_banner", "-i", file, "-ar", "44100", \
                                                   "-ac", "2", "-vcodec", "copy", dst_file_path ], \
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()


get_file_lists( work_dir, SRC_TYPE )
threads = []
threading.Semaphore(4)
for item in file_lists:
    t = threading.Thread(target = convert_to_dst_type, args=[item, SRC_TYPE, DST_TYPE])
    threads.append(t)

n=0
for t in threads:
    t.setDaemon(True)
    t.start()
    n=n+1

    while True:
        if (len(threading.enumerate()) < 5):
            break

for t in threads:
    t.join()



