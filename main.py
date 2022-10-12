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
import argparse
import random
import datetime

from  InputArgParse                 import ParseInputArgs
from  downloader.Downloader         import Downloader
from  filemanager.FileManager       import FileManager
from  mediaprocessor.MediaProcessor import MediaProcessor
from  uploader.Uploader             import Uploader
from  facer.Facer                   import Facer


intent = ParseInputArgs( )

downloader = Downloader(
        operate     = intent.operate,
        platform    = intent.platform,
        data        = intent.data,
        dataType    = intent.dataType,
        userId      = intent.userId,
        pcursor     = intent.pcursor,
        productMax  = intent.productMax,
        pmax        = intent.pmax,
        playbackUid = intent.playbackUid,
        playbackMax = intent.playbackMax,

        )
filemanager = FileManager(
        srcDir          = intent.srcDir,
        dstDir          = intent.dstDir,
        operate         = intent.operate,
        platform        = intent.platform,
        fileManagerData = intent.fileManagerData,
        password        = intent.zipPassword

        )
mediaprocessor = MediaProcessor( 
        srcDir          = intent.srcDir,
        dstDir          = intent.dstDir,
        pmax            = intent.pmax,
        operate         = intent.operate, 
        platform        = intent.platform
        )
uploader = Uploader(
        srcDir           = intent.srcDir,
        operate          = intent.operate,
        platform         = intent.platform
       )

facer    = Facer(
        srcDir           = intent.srcDir,
        operate          = intent.operate,
        platform         = intent.platform
       )

print('operate:', intent.operate)
print('platform:', intent.platform)
print('data:', intent.data)
print('dataType:', intent.dataType)
print('userId:', intent.userId)
print('pcursor:', intent.pcursor)
print('productMax', intent.productMax)
print('pmax', intent.pmax)
print('playbackUid', intent.playbackUid)
print('playbackMax', intent.playbackMax)

print('----------------filemanager----------------')

print('operate:', intent.operate)
print('platform:', intent.platform)
print('srcDir:', intent.srcDir)
print('dstDir:', intent.dstDir)
print('fileManagerData:', intent.fileManagerData)
print('password:', intent.zipPassword)
print('--------end--------filemanager----------------')



downloader.Run()
filemanager.Run()
mediaprocessor.Run()
uploader.Run()
facer.Run()




