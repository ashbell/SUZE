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
from xpinyin import Pinyin

## rename all mp4 file

src_dir = 'F:\\vc\\'

dir_list = os.listdir(src_dir)

name_dir = []
for alpha in dir_list:
    alpha_dir = src_dir + alpha + '\\'
    name_dir_list = os.listdir(alpha_dir)
    for name in name_dir_list:
        name_dir_path = alpha_dir+name+'\\'
        if os.path.isdir(name_dir_path):
            name_dir.append(name_dir_path)

for name_path in name_dir:
    mp4_dir_path = name_path + 'mp4\\'
    if not os.path.exists(mp4_dir_path):
        print('Not found mpe dir, %s'% mp4_dir_path )
    else: 
        mp4_files = os.listdir(mp4_dir_path)
        print('----------------------%s--------------------' % mp4_dir_path)
        for mp4 in mp4_files:
            if '.mp4' in mp4:
                mp4_path = mp4_dir_path + mp4
                new_file_name = 'A' + mp4
                new_file_path = mp4_dir_path + new_file_name
                print('%s---%s'%(mp4_path, new_file_path))
                shutil.move(mp4_path, new_file_path)
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')
    ##input('>')




