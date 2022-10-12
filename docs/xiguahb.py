#!/usr/bin/env   python

import os
import sys

""" useage: ./xiguahb.py  dir"""
if sys.argv[1] != '':
    src = sys.argv[1]
    if src[-1] != '/':
        src = src + '/'
mp4a_list = []
def file_list(src):
    for root, dirs, files in os.walk(src, topdown=False):
        for name in files:
            if ('mp4a' in name) and ('no_water' in name): 
                mp4a = os.path.join(root,name)
                mp4 = mp4a.replace('mp4a','mp4')
                if os.path.exists(mp4):
                    mp4a_list.append(mp4a)

file_list (src)

for file in mp4a_list:
    mp4a = file
    mp4 = mp4a.replace('mp4a','mp4')
    out = mp4.replace('.mp4', '_comb_.mp4')
    cmd = 'ffmpeg -i ' + mp4 + ' -i ' + mp4a + ' -vcodec copy -acodec copy ' + out
    os.system(cmd)
    print('>>>>>>>: %s' % out)
