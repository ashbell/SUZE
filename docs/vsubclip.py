#!/usr/bin/env  python

import os
import sys
import time
import threading
from time import ctime, sleep
import subprocess

##  ./vsubclip.py  ./srt/   ./video/

fmts=['.mp4','.ts']
out_path = './out/'
max_thread = 4
bash_path = "C:\\cygwin64\\bin\\mintty.exe"
ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"


srt_dir = sys.argv[1]
video_dir = sys.argv[2]

if not os.path.exists( out_path ):
    os.makedirs( out_path )

if srt_dir[-1] != '/':
    srt_dir = srt_dir + '/'

if srt_dir[-1] != '/':
    video_dir = video_dir + '/'

srt_file = os.listdir( srt_dir )

srt_path = []
video_path = []
options = []
for srt in srt_file:
    if 'srt' in srt:
        srt_path.append( srt_dir + srt )
        file_name = video_dir + srt.split('.')[0]
        for fmt in fmts:
            files = file_name + fmt
            if os.path.exists(files):
                video_path.append ( files )

for file in srt_path:
    fd = open(file, 'r', encoding='UTF-8')
    lines = fd.readlines()
    clip_count = 0
    fd.close()
    for l in lines:
        l.strip('\n')
        if '-->' in l:
            clip_count = clip_count + 1
            ss = l.split(',')[0]
            tt = l.split(',')[1].split('>')[1].split(',')[0].strip(' ')
            ## fuck the space, lead ffmpeg can't work, "-to ___00:22:22"

            ## ./srt/001.srt
            video_name = video_dir + file.split('/')[2].split('.')[0]
            for fmt in fmts:
                tmp = video_name +fmt
                if os.path.exists(tmp):
                    video_file = tmp

            ## out file name
            str_num = '%03d' % clip_count 

            file_name = file.split('/')[2].split('.')[0]
            file_type = '.'+video_file.split('.')[-1]
            out_file = out_path + file_name + '_clip_' + str_num + file_type 
            argv = [ file, video_file, ss, tt, out_file ]
            options.append(argv)


def clip_video(op):
    ## op ['./srt/041.srt', './video/041.mp4', '00:25:25', ' 00:28:52', './video/041_clip_003.mp4']
    ## ffmpeg -ss 00:01:00 -to 00:02:00  -i input.mp4 -c copy output.mp4    
    """
    for i in op:
        print(op[2]+'-->'+op[3]+'-->'+op[1]+'--->'+op[4])
    """

    p =  subprocess.Popen([bash_path, ffmpeg_path, "-hide_banner", "-ss", op[2], "-to", op[3], \
                                                   "-i", op[1], "-c", "copy", op[4] ], \
         stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    shell_out = p.stdout.read()
    shell_error = p.stderr.read()

threads = []
threading.Semaphore(4)
for op in options:
    t = threading.Thread(target = clip_video, args=[op])
    threads.append(t)

n=0
for t in threads:
    t.setDaemon(True)
    t.start()
    print("%s processing option:  %s" % (t,options[n]))
    n=n+1

    while True:
        if (len(threading.enumerate()) < 5):
            break

for t in threads:
    t.join()



