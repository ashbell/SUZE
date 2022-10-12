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

src_dir = 'F:\\ks.dir\\flows\\has_mp4\\'
src_lists = os.listdir(src_dir)

dst_dir = 'E:\\vc\\'

fd_names = open('./allinfo', 'r', encoding='utf-8')
names = fd_names.readlines()
fd_names.close()

forbidden = ['\\', '/',':', '*','?', '<', '>', '|']

dict_name = {}

chinese_name = []

for name in names:
    name = name.strip('\n')
    str_name = name.split('----')[1]
    uid = name.split('----')[0].replace(' ', '')
    nick_name = str_name.split('--')[0].replace(' ','')
    lens = len(nick_name)

    lst_name = list(nick_name)
    for num in range(0, lens):
        if nick_name[num] in forbidden:
            lst_name[num] = '_'
    nick_name = ''.join(lst_name)
    dict_name[uid] = nick_name
    chinese_name.append(nick_name)

##chinese_name = ['《🌺🌺春暖花开🌸》','L雅宝💋不忘初心']
chinese_name = os.listdir(dst_dir)

alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
         'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

digit = ['0','1','2','3','4','5','6','7','8','9']
legal_name = []

move_info = {}

def get_legal_name(val):
    str_legal_name = ''
    lst_val = list(val)
    lst_name = []
    for char in lst_val:
        if ('\u4e00' <= char <= '\u9fff'):
            lst_name.append(char)
        if char in alpha:
            lst_name.append(char)
        if char in digit:
            lst_name.append(char)

    str_legal_name =''.join(lst_name)
    p = Pinyin()
    first_alpha = p.get_pinyin(str_legal_name)[0].upper()
    dir_name = first_alpha + str_legal_name

    ##print('%s\t: %s'%(val, dir_name))
    return dir_name
##print(len(chinese_name))
for init_name in chinese_name:
    if len(init_name) == 1:
        pass
    else:
        legal_dir_name = get_legal_name(init_name)    
        alpha_dir_name = legal_dir_name[0]
        alpha_path = dst_dir + alpha_dir_name + '\\'
        init_path  = dst_dir + init_name + '\\'
        if not os.path.exists(alpha_path):
            os.makedirs(alpha_path)
        dst_path = alpha_path + legal_dir_name + '\\'
        print('%s ----------------->%s' %(init_path, dst_path))
        ##shutil.move(init_path, dst_path)
        


def move_dir(src, dst):
    print('Move   %s\tto\t%s ' %(src, dst))
    ##shutil.move(src, dst)


unknow_uid = []
fd_unknow = open('./unknow', 'a+', encoding='utf-8')

for src in src_lists:
    src_path = src_dir + src +'\\'
    uid = src_path.split('\\')[-2]
    if uid in dict_name.keys():
        dir_name = dict_name[uid]
        dst_path = dst_dir + dir_name + '\\'
        
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        uid_file = dst_path + uid + '.txt'
        fw = open(uid_file, 'a+', encoding='utf-8')
        fw.close()
        ##print(uid_file)
        ##move_dir(src_path, dst_path)

    else:
        fd_unknow.write(uid+'\n')
fd_unknow.close()








