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
import random

src_dir = 'F:\\ksdown.class\\ks_dir\\'
dst_dir = 'F:\\vc\\'
NAME_FILE = 'F:\\ksdown.class\\ids\\allinfo'

alpha = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
         'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

digit = ['0','1','2','3','4','5','6','7','8','9']

def get_uid_name_dict(name_file = ''):
    uid_legal_name = {}
    fnames = open(name_file, 'r', encoding='utf-8')
    names = fnames.readlines()
    fnames.close()

    for name in names:
        name = name.strip('\n')
        legal_name = []
        if len(name) > 0: 
            split_name = name.split('----')
            origin_name = split_name[1].replace(' ', '')
            uid = split_name[0].replace(' ','')

        ''' 如果改了名字，会有两个名字段, 取第一个'''
        history_names = origin_name.split('--')
        first_name = history_names[0]

        name_len = len(first_name)
        list_name = list(first_name)
        for char in list_name:
            if ('\u4e00' <= char <= '\u9fff'):
                legal_name.append(char)
            if char in alpha:
                legal_name.append(char)
            if char in digit:
                legal_name.append(char)
        str_legal_name = ''.join(legal_name)
        ##print('%s--%s'%(uid, str_legal_name))
        uid_legal_name[uid] = str_legal_name

    return uid_legal_name

def get_uid_alpha_name():
    uid_alpha_name = {}
    name_dict = get_uid_name_dict(NAME_FILE)

    p = Pinyin()
    for uid in name_dict.keys():
        first_alpha = p.get_pinyin(name_dict[uid])[0].upper()
        dir_name = first_alpha + name_dict[uid]
        uid_alpha_name[uid] = dir_name
        ##print('%s--%s--%s' %(uid,name_dict[uid], dir_name))
    return uid_alpha_name

def get_uid_alpha_path():
    uid_alpha_path = {}
    uid_alpha_dir = get_uid_alpha_name()
    for uid in uid_alpha_dir:
        first_alpha = list(uid_alpha_dir[uid])[0]
        alpha_path = dst_dir + first_alpha + '\\'
        if not os.path.exists(alpha_path):
            os.makedirs(alpha_path)

        path = alpha_path + uid_alpha_dir[uid] + '\\'  
        uid_alpha_path[uid] = path
        ##print('%s--%s'%(uid,path))
    return uid_alpha_path

def map_to_dst_dir():
    bash = 'F:\\mvmp4.sh'
    uids = os.listdir(src_dir)
    dict_path = get_uid_alpha_path()
    for uid in uids:
        old_dir = os.getcwd()
        if ('3x' in uid) and (uid in dict_path.keys()):
            src_path = src_dir + uid +'\\'
            dst_path = dict_path[uid] + uid + '\\'
            uid_file = dict_path[uid] + uid+ '.txt'
            mp4_path = dict_path[uid] + 'mp4\\'
            if not os.path.exists(mp4_path):
                os.makedirs(mp4_path)
            ''' 因为move方法当目标文件夹已经存在时候，他会直接覆盖删除，导致原来的文件被删除'''
            if os.path.exists(dst_path):
                dst_path = dict_path[uid] + uid + '_'+str(random.randint(10,99)) + str(random.randint(0,9)) +'\\'
            print('%s--%s'%(src_path, dst_path))
            shutil.move(src_path, dst_path)
            fw = open(uid_file,'w', encoding='utf-8')
            fw.close()
            ##input('>>>')
            os.chdir(dst_path)
            new_dir = os.getcwd()
            cmd = "C:\\cygwin64\\bin\\mintty.exe " + " "+ bash + " " + new_dir
            p = subprocess.Popen(cmd, \
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
            shell_out = p.stdout.read()
            shell_error = p.stderr.read()
            os.chdir(old_dir)
            ##input('>>>')

            

map_to_dst_dir()
    
        

       


