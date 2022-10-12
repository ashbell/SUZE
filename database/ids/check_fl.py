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

fneed = open('./not_in', 'r',encoding='utf-8')
needs = fneed.readlines()
fneed.close()

fall = open('./need.4-updating', 'r', encoding='utf-8')
alls = fall.readlines()
fall.close()

lst_need = [x.strip('\n').split('----')[0].replace(' ','') for x in needs]
lst_all  = [x.strip('\n').split('----')[0].replace(' ','') for x in alls]

not_in = []

for need in lst_need:
    if need in lst_all:
        pass
    else:
        not_in.append(need)

fw = open('./need_to_update', 'w+', encoding='utf-8')
for val in not_in:
    fw.write(val + '\n')
fw.close()

