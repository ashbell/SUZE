#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import re
import base64
import subprocess
import time
import wget
import threading
import urllib.request
import codecs
import re

fd_old = open('./old', 'r', encoding='utf-8')
old_list = fd_old.readlines()
fd_old.close()

fd_new = open('./myflos', 'r', encoding='utf-8')
new_list = fd_new.readlines()
fd_new.close()

lists = []
name_info = {}
for val in old_list:
    val = val.strip('\n')
    name = val.split('>')[0]
    uid = val.split('/')[-1]
    name_info[uid] = [name]
    
##print(name_info)

for val in new_list:
    val = val.strip('\n')
    name = val.split('>')[1].replace(' ','')
    uid = val.split('>')[0].replace(' ','')
    if uid in name_info.keys():
        name_info[uid].append(name)
    else:
        name_info[uid] = [name]

    
fw = open('./allinfo', 'w+', encoding='utf-8')
for val in name_info.keys():
    info = ''
    if len(name_info[val]) > 1:
        for name in name_info[val]:
            info = info + name + '--'
    else:
        info = name_info[val][0]
    final_info = '%s ----  %s' % (val, info)
    fw.write(final_info+'\n')


fw.close()
