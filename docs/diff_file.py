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

f1 = open('./not_in', 'r', encoding='utf-8')
r1 = f1.readlines()
f1.close()

f2 = open('./has.2', 'r', encoding='utf-8')
r2 = f2.readlines()
f2.close()

x1 = [x.strip('\n') for x in r1]
x2 = [x.strip('\n') for x in r2]
for line1 in x1:
    if line1 not in x2:
        print(line1)
