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
from xpinyin import Pinyin
from moviepy.editor import  VideoFileClip
from moviepy.editor import *
from pymediainfo import MediaInfo
from pprint import pprint
import mimetypes
##import magic
import easyocr
import cv2


## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')

words = (open('./user', 'r', encoding='utf-8')).readlines()

fail = 0

uid = './uid'
if os.path.exists(uid):
    fd = open(uid, 'a+', encoding='utf-8')
else:
    fd = open(uid, 'w+', encoding='utf-8')

for word in words:
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
        print('------------------------------------------------------')
        print(r.text)
        try:
            data = json.loads(r.text)
            user_id= data['data']['visionSearchUser']['users'][0]['user_id']
            user_name= data['data']['visionSearchUser']['users'][0]['user_name']
            fail = 0
            info = '%s -- %s --%s\n' % (word, user_id, user_name)
            print(info)
            fd.write(info)
        except:
            fail = fail + 1
            print('%s    -    Canot Get user_id!\n' % word)

        if fail > 5:
            print('Fail to many, exit')
            exit()
        secs = random.randint(0, 5) + random.randint(6,9)
        time.sleep( secs ) 
fd.close()
