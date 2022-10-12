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
"""
from xpinyin import Pinyin
from moviepy.editor import  VideoFileClip
from moviepy.editor import *
from pymediainfo import MediaInfo
from pprint import pprint
import mimetypes
##import magic
import easyocr
import cv2
"""

"""
    ./query  userid_file    databasefile
    用网页搜索的方式，查询userid_file 里面的ID，得出uid， 如果找不到，则标记出是哪个视频
    标记的数据库databsefile
    
"""
userid_file = ''
if len(sys.argv) == 3:
    userid_file = sys.argv[1]
    database = sys.argv[2]
else:
    print('No userid_file or database file  specified!')
    exit()
## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')


def  load_database_to_dict(datafile = ''):
    if os.path.exists(datafile):
        f = open(datafile, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        database = {}
        mp4id = []
       
        num = 0
        total = len(lines)
        while num < total:
            line = lines[num].strip('\n')
            if  line[-4:] == '.mp4':
                mp4id.append(num)

            num = num + 1
       
        mp4_count = len(mp4id)
        for idx in range(0, mp4_count):
            curr_mp4_idx = mp4id[idx]
            ##print('%d -- %s' %(curr_mp4_idx, lines[mp4id[idx]]))
            mp4_file = lines[curr_mp4_idx].strip('\n')
            if (idx + 1) < mp4_count:
                next_mp4_idx = mp4id[idx+1] 
            else:
                next_mp4_idx = total 
            
            if lines[curr_mp4_idx] in database.keys():
                pass
            else:
                database[mp4_file] = []

            if next_mp4_idx - 1 == curr_mp4_idx:
                database[mp4_file].append('None')
            else:
                for p in range(curr_mp4_idx+1, next_mp4_idx):
                    user_id = lines[p].strip('\n')
                    if len(user_id) > 2:
                        user_id = user_id[2:]
                        database[mp4_file].append(user_id)                
        
        return database


def  query_from_web(word = '', mp4_file=''):
    fail = 0
    uid = './uid'
    if os.path.exists(uid):
        fd = open(uid, 'a+', encoding='utf-8')
    else:
        fd = open(uid, 'w+', encoding='utf-8')

    word = word.strip('\n')
    if (word != '') and (word != 'None') and (len(word) > 7):
        header = {
            'Cookie': '''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpf=PC_WEB; kpn=KUAISHOU_VISION; ksliveShowClipTip=true; userId=2183004766; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABDwbDPyeAjQsich9sRqi8qn2wWKO6kigHN0CHePFhd5UoRoQQp1sW8csU3jwYPZkuW8xq9sPT-TuxqyfJ6aEnfnIcQCnClmPV9xmZK1urIZwDic7jOe-Uwn8YzvdSX9goNxCuRhtiTQRphWZ5N9ucqxwbmsLcLu6Zfoynu9tBmZ-CcpPXd1DiuQv6A1_4lmdyAkz12yRN2YE7JPAe_bvd_RoSKS0sDuL1vMmNDXbwL4KX-qDmIiDQCDcIwwU77Z6pMle9ISU7N0O-t4OworzXfYxo86V8EigFMAE; kuaishou.server.web_ph=b995c61d13edc610e5745c59a4064c019ca8''',
            'Host':'www.kuaishou.com',
            'Origin':'https:/www.kuaishou.com',
            'Referer':'https://www.kuaishou.com/search/author?searchKey=' + word,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }

        query_json = {
            "operationName":"graphqlSearchUser","variables":{"keyword":word},"query":"query graphqlSearchUser($keyword: String, $pcursor: String, $searchSessionId: String) {\n  visionSearchUser(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId) {\n    result\n    users {\n      fansCount\n      photoCount\n      isFollowing\n      user_id\n      headurl\n      user_text\n      user_name\n      verified\n      verifiedDetail {\n        description\n        iconType\n        newVerified\n        musicCompany\n        type\n        __typename\n      }\n      __typename\n    }\n    searchSessionId\n    pcursor\n    __typename\n  }\n}\n"
        }

        r = requests.post('https://www.kuaishou.com/graphql', headers=header, json=query_json)
        try:
            data = json.loads(r.text)
            user_id= data['data']['visionSearchUser']['users'][0]['user_id']
            user_name= data['data']['visionSearchUser']['users'][0]['user_name']
            fail = 0
            info = '%s -- %s --%s--%s\n' % (word, user_id, user_name, mp4_file)

        except:
            fail = fail + 1
            info = '%s -- %s -- Canot Get user_id!\n' % (word, mp4_file )
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(r.text)
            print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        
        print(info.strip('\n'))
        if mu.acquire(True):
            fd.write(info)
            fd.close()
            mu.release()

        if fail > 5:
            print('-----------------------------------------------------------------------------')
            print('%s - %s - Failed too many times, Exit!\n' % (word, mp4_file ))
            print(r.text)
            print('-----------------------------------------------------------------------------')
            fd.close()
            exit()
        secs = random.randint(0, 5) + random.randint(6,9)
        time.sleep( secs ) 

def  get_mp4_from_userid(user_id):
    mp4_file = ''
    dicts = load_database_to_dict(database)
    for mp4_file in  dicts.keys():
        lst = dicts[mp4_file]
        for ele in lst:
            if user_id in ele:
                return mp4_file


def  find_without_text():
    dicts = load_database_to_dict(database)
    for mp4_file in  dicts.keys():
        lst = dicts[mp4_file]
        for ele in lst:
            if 'None' in ele:
                print( mp4_file )
                print(lst)

    
find_without_text()


"""

fd_user = open(userid_file, 'r', encoding='utf-8')
words = fd_user.readlines()
fd_user.close()

mu  = threading.Lock()


threads = []
for word in words:
    word = word.strip('\n')
    mp4_file = get_mp4_from_userid(word)

    t = threading.Thread(target=query_from_web, args=[word, mp4_file ])
    threads.append(t)

for t in threads:
    t.daemon = True
    t.start()
    while(True):
        if len(threading.enumerate()) < 2:
            break
for t in threads:
    t.join()
    

"""




