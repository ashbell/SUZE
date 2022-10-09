#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import json
import re
import time
import wget
import codecs
import datetime
import random
import threading
import requests
import base64
import subprocess
import urllib.request
from urllib.parse import unquote
from threading import Thread,Lock

from downloader.Headers import  Headers 

##headers = Headers('3xss', '1E2')
##print(headers.common_header)
''' C:\\SUZE\\out\\ksuid\\3xxxxx\\video\\'''
class Downloader( object ):
    def __init__( self, operate, platform, data, dataType, 
                  userId, pcursor, productMax, pmax, playbackUid, playbackMax, ):
        self.cwd = os.getcwd() + '\\'
        self.defaultDstDir = self.cwd + 'out\\'
        self.ksUidDir = self.defaultDstDir + 'ksuid\\'
        self.ksPlaybackDir = self.defaultDstDir + 'ksplayback\\'
        self.ksPlaybackUid = playbackUid
        self.ksPlaybackUidDir = self.ksPlaybackDir + self.ksPlaybackUid  + '\\'
        self.inputDstDir = ''
        self.authorName = ''
        self.pmax = pmax
        self.productMax = productMax
        self.playbackMax= playbackMax
        self.jsonFiles=[]
        self.urls=[]
        self.downInfos= {}
        self.operate = operate
        self.platform = platform
        self.data = data
        self.dataType = dataType
        self.userId = userId
        self.pcursor = pcursor
        self.videoCnt = 0
        self.myUserId = '3xnzffmzps58emw'
        self.myFeedsDir = self.cwd + 'database\\'
        self.myFeedsFile = self.myFeedsDir + self.myUserId + '.feeds' 
        self.myFeeds = { } ### { uid: nick_name }
        self.postUrl = 'https://www.kuaishou.com/graphql'
        self.ksLiveBroadcastUrl = 'https://live.kuaishou.com/rest/wd/live/liveStream/myfollow'
        self.playbackPostUrl = 'https://live.kuaishou.com/live_graphql'
        self.playbackVideoUrlPre = 'https://live.kuaishou.com/playback/'
        self.ksUidRootDir = self.ksUidDir + self.userId + '\\'
        ##self.ksUidVideoDir = self.ksUidRootDir + 'video\\'
        self.ksPlaybackUrls = []
        self.ksM3u8Urls = []
        self.ksM3u8Files = []
        self.ksM3u8HttpHostPre = { } ## m3u8 url pre as ts file's prefix, m3u8file: prefix
        self.pageCnt = 0
        self.retry = 0
        self.maxTry = 5   ## If error same than 5 times, exit.
        self.dyMyUid = 'MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz'
        self.dyDataDir = self.defaultDstDir + 'dy' + '\\'
        self.dyMyFeedsDir = self.dyDataDir + 'myfeeds\\'
        self.dyMyFeedsUidFile = self.dyDataDir + 'mydy.feeds'
        self.dyUserPageUrl = 'https://www.douyin.com/user/'
        self.dyLiveStatusReg = '>直播中<'
        self.dyLiveRoomIdReg = 'live.douyin.com/\d+\?'
        self.dyFlvReg = 'flv_pull_url.*?\.flv'
        self.dyRoomTitleReg = '<title .*</title>'
        self.dyMyFeedsMainPageFiles = []
        self.dyLiveRoomUrls = { }  ## livinguidFile:liveRoomUrl
        self.dyLiveRoomPageFiles = [] ## livingroom file
        self.dyTitleLvingFlvs = { } ## roomtitle: flv url
        print( '<Initialize Downloader>  %s  %s Pcursor: %s' %  (self.userId, self.dataType, self.pcursor) )
    
    def DownloadPrepare( self  ):
        if self.userId != '':
            self.ksUidRootDir = self.ksUidDir + self.userId + '\\'
        self.ksUidVideoDir = self.ksUidRootDir + 'video\\'
        ##print('uidRootdir: %s' % self.ksUidVideoDir)
        if not os.path.exists( self.ksUidRootDir ):
            os.makedirs( self.ksUidRootDir )
        if not os.path.exists( self.ksUidVideoDir ):
            os.makedirs( self.ksUidVideoDir )
        if not os.path.exists( self.myFeedsDir ):
            os.makedirs( self.myFeedsDir )

        if not os.path.exists( self.ksPlaybackDir ):
            os.makedirs( self.ksPlaybackDir )
        if not os.path.exists( self.ksPlaybackUidDir ):
            print( self.ksPlaybackUidDir)
            os.makedirs( self.ksPlaybackUidDir )
        if not os.path.exists( self.dyMyFeedsDir ):
            os.makedirs( self.dyMyFeedsDir )
        if not os.path.exists( self.dyDataDir ):
            os.makedirs( self.dyDataDir )
        if not os.path.exists( self.myFeedsFile ):
            with open( self.myFeedsFile, 'w+', encoding='utf-8' ) as f:
                pass

    def DownloadVideos( self, url, path ):
        ret = subprocess.call( ['wget', '-O', path, url], 
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT )

    ''' write string data to file '''
    def Writer( self, data, wfile, mode='' ):
        if mode == 'wb':
            with open( wfile, mode ) as f:
                f.write( data )
        else:
            with open( wfile, mode, encoding='utf-8' ) as f:
                f.write( data )
   

    ''' read file, return lines[]'''
    def Reader( self, rfile ):
        lines = []
        with open( rfile, 'r', encoding='utf-8' ) as f:
            lines = f.readlines()
        return lines
            
    ''' fectch json file from webserver, save file to local, save file path to self.jsonFiles[]'''
    def KsFetchHttpResponse( self, userId, pcursor ):
        limit   = self.productMax/20 + 1
        pageCnt = 0
        second  = 0
        while pcursor != 'no_more':
            print('  <KsFetchHttpResponse> %s : %s' % 
                    (userId, pcursor )
                 )
            oldPcursor = pcursor
            self.headers = Headers( userId, pcursor )
            r = requests.post( self.postUrl, 
                               headers = self.headers.common_header, 
                               json = self.headers.user_product_json
                             )
            r.encoding = 'utf-8'
            data = r.text
            if len(data) != 0:
                pageCnt = pageCnt + 1
                jsname = "%04d" % pageCnt
                jsfilename = self.ksUidRootDir + jsname + '.json'
                self.Writer( data, jsfilename, 'w+' )
                self.jsonFiles.append( jsfilename )
            else:
                print( '  <E>Error when read data from webserver. exit!')
                exit()
                
            jsondata = json.loads(data)
            try:
                pcursor = jsondata['data']['visionProfilePhotoList']['pcursor']
            except:
                print('  <W>Failed to parse pcursor!')
                pcursor = oldPcursor
                self.retry = self.retry + 1
            if self.retry > self.maxTry:
                print('  <E>Failed to Get pcursor too many times, eixt!')
                exit()

            if pageCnt > limit:
                print('  <MaxDownload limit  Reach!')
                break
            second = random.randint(5,10) +random.randint(0,5)
            time.sleep( second )

    ''' get video url from jsonFiles.'''
    def KsGetVideoUrlsFromJsonFile( self, jsonFiles=[] ):
        try:
            for jsfile in jsonFiles:
                f = open( jsfile, 'r', encoding='utf-8' )
                data = json.load( f )
                f.close()
                if self.authorName != '':
                    self.authorName = data['data']['visionProfilePhotoList']['feeds'][0]['author']['name']
                videoPages = len( data['data']['visionProfilePhotoList']['feeds'] )

                for id in range( videoPages ):
                    videoTitle = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['caption']
                    if len( videoTitle ) == 0:
                        videoTitle = 'null_title'
                    try:
                        url = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource']\
                                  ['hevc']['adaptationSet'][0]['representation'][0]['url']
                        vid = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource']['hevc']['videoId']
                    except:
                        url = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource'] \
                                  ['h264']['adaptationSet'][0]['representation'][0]['url']
                        self.videoCnt = self.videoCnt + 1
                        vid = "%04d" % self.videoCnt 

                    if (url != '') and (vid != ''):
                        videoPath = self.ksUidVideoDir + vid + '.mp4'
                        self.downInfos[videoPath] = url
        except:
            print('  <E>Error when Parse vid/url in Jsonfile.')
            exit()
    ''' get author name, sava uid-name to userinfo'''
    def KsGetAuthorName( self ):
        try:
            with open( self.jsonFiles[0], 'r', encoding='utf-8') as f:
                data = json.load( f )
            self.authorName = data['data']['visionProfilePhotoList']['feeds'][0]['author']['name']
        except:
            self.authorName = 'GET_AUTHORNAME_FAILED'
        print(self.authorName)
        uidFile = self.ksUidRootDir + self.userId + '.txt'
        string = '%s --> %s' % (self.userId, self.authorName)
        self.Writer( self.authorName, uidFile, 'a+' )
        
    ''' download video use mutilthread '''         
    def KsMutilPhreadDownload( self ):
        print('    <KsMutilPhreadDownload: -pmax -> %s' % self.pmax)
        threads = []
        pmax    = int( self.pmax )
        n = 0
        for v in self.downInfos.keys():
            t = threading.Thread( target = self.DownloadVideos,
                                  args   = [ self.downInfos[v], v ] )
            t.setName( '    <Thread-%04d.......Download.....%s >' % 
                       (n, v) )
            n = n + 1
            threads.append( t )
        for t in threads:
            t.deamon = True
            t.start()
            print(t.getName())
            while True:
                if len( threading.enumerate() ) < pmax:
                    break
        for t in threads:
            t.join()

    ''' fetch my all feeds uid and nickname, save them to local file as database.'''
    def KsGetAllFeeds( self, userId, pcursor ):
        while    pcursor != 'no_more' :
            print( '  <KsGetAllFeeds> %s :  Pcursor: %s' % (userId, pcursor) ) 
            oldPcursor = pcursor
            self.headers = Headers( userId, pcursor )
            r = requests.post( self.postUrl, 
                               headers = self.headers.myfols_header, 
                               json=self.headers.myfols_header_json )
            r.encoding='utf-8'
            data=r.text
            if len( data ) > 0:
                self.pageCnt = self.pageCnt + 1
                jsname = "%04d" % self.pageCnt
                jsonfile = self.myFeedsDir + jsname + '.json'
                self.Writer( data, jsonfile, 'w+' )
                self.jsonFiles.append( jsonfile )

            try: 
                jsondata = json.loads( data )
                pcursor = jsondata['data']['visionProfileUserList']['pcursor']
            except:
                print('    <E>Failed to Get pcursor.....')
                pcursor = oldPcursor
            time.sleep( 2 )

        try:
            for js in self.jsonFiles:
                with open( js, 'r', encoding='utf-8' ) as f:
                    jsondata = json.load( f )

                feeds = jsondata['data']['visionProfileUserList']['fols']
                lenfeeds = len( feeds )
                for num in range( 0, lenfeeds ):
                    uid  = jsondata['data']['visionProfileUserList']['fols'][num]['user_id']
                    name = jsondata['data']['visionProfileUserList']['fols'][num]['user_name']
                    info = '%s --> %s\n' % (uid, name) 
                    self.Writer( info, self.myFeedsFile, 'a+' )
            print('  <KsGetAllFeeds> - Done.')
        except:
            print('  <E>Faild to Get uid/name!')
    
    ''' fetch my all feed live stream. print them to teminal.'''
    def KsGetLiveStream( self ):
        print('  <KsGetLiveStream>   --  %s' % self.myUserId )
        header = Headers( self.myUserId, '' )
        req = urllib.request.Request( self.ksLiveBroadcastUrl, 
                                      headers=header.myfollow_live_header )
        htmlContent = urllib.request.urlopen( req ).read()
        htmlFile    = self.myFeedsDir + self.myUserId + '.live'
        self.Writer( htmlContent, htmlFile, 'wb' )

        try:
            jsondata    = json.loads( htmlContent )
            data        = jsondata['follow']
            count       = len( data )
        except:
            print('    <E> Error When load jsonfiles!')
            exit()

        for num in range( 0, count ):
            name = data[num]['user']['user_name']
            liveUrl = data[num]['playUrls'][0]['url']
            millsTime = data[num]['startTime']
            eid = data[num]['user']['eid']
            strTime = time.strftime( '%Y-%m-%d_%H_%M_%S', time.localtime(millsTime/1000) )
            print('%s - : %s' % (liveUrl, name) )

    
    ''' fetch playback video json files, will download all videos json, save it.'''
    def KsFetchPlaybackVideoJsonFiles( self, userId, pcursor ):
        ''' every json page has 8 videos'''
        limit = round(self.playbackMax/8) + 1
        ##print('limit: %s' % limit)
        while  pcursor != 'no_more':
            header = Headers( userId, pcursor )
            print( '  <KsFetchPlaybackVideoJsonFiles>  - %s  - %s ' 
                   % ( userId, pcursor)
                 )
            oldPcursor = pcursor
            r = requests.post( self.playbackPostUrl, 
                               headers=header.playback_header, 
                               json=header.playback_json )
            r.encoding = 'utf-8'
            data = r.text
            if len( data ) > 0: 
                self.pageCnt = self.pageCnt + 1
                filename = "%04d" % self.pageCnt
                jsonfile = self.ksPlaybackUidDir + filename + '.json'
                self.Writer( data, jsonfile, 'w+' )
                self.jsonFiles.append( jsonfile )
                jsondata = json.loads( data )
                oldPcursor = pcursor
                try:
                    pcursor = jsondata['data']['playbackFeeds']['pcursor']
                    self.retry = 0
                except:
                    print('    <E>Error when get pcursor!')
                    pcursor = oldPcursor
                    self.retry = self.retry + 1
            else:  
                print(    '<E>Fetch data error from webserver!' )
                self.retry = self.retry + 1

            if self.retry > self.maxTry:
                print( '    <E>Fetch data error from webserver - Too many times, exit!' )
                exit()
            if self.pageCnt >= limit:
                print('    <I>Limit video Fetch Reached!' )
                break
            time.sleep(3)

    ''' get video urls from json files.'''
    def KsGetVieoUrlsFromJsonFiles( self ):
        ##print('poruductMax: %s' % self.playbackMax)
        try:
            for js in self.jsonFiles:
                with open( js, 'r', encoding='utf-8' )  as f:
                    jsondata = json.load( f )
                length = len( jsondata['data']['playbackFeeds']['list'] )
                for num in range( 0, length ):
                    vid = jsondata['data']['playbackFeeds']['list'][num]['productId']
                    if vid != '':
                        self.ksPlaybackUrls.append( self.playbackVideoUrlPre + vid )
                        self.videoCnt = self.videoCnt + 1
                    if self.videoCnt >= self.playbackMax:
                        break
        except:
            print('    <E>Errot when parse json files to get video url!')
            exit( )

        for url in self.ksPlaybackUrls:
            print('\t\t-DB: %s' % url)

    ''' get m3u8 file from video/product ID, save html and m3u8 to local.'''
    def KsGetM3u8File( self ):
        m3u8Reg = 'm3u8Url.*__typename'
        for url in self.ksPlaybackUrls:
            header      = Headers( self.userId, '' )
            htmlname    = url.split('/')[-1]
            htmlfile    = self.ksPlaybackUidDir + htmlname + '.html'
            m3u8file    = self.ksPlaybackUidDir + htmlname + '.m3u8'

            req = urllib.request.Request(url,  headers=header.playback_m3u8_header )
            htmlContent = urllib.request.urlopen(req).read()
            
            ##data = html_content.decode('UTF-8')
            ##data = html_content.decode("unicode-escape")  
            ''' convert unicode to string, but chinese is fuck!  '''
            ''' utf8 = codecs.decode(html_content, 'utf-8')  convert to Chinese  '''
            self.Writer( htmlContent, htmlfile, 'wb' )

            data    = htmlContent.decode( "unicode-escape" )  
            m3u8    = re.findall( m3u8Reg, data )
            m3u8Url = 'https:' + m3u8[0].split(',')[0].split(':')[2].replace('\"','')
            ##print(m3u8_url)

            self.ksM3u8Urls.append( m3u8Url )
            if os.path.exists( m3u8file ):
                os.remove(m3u8file)
            wget.download( m3u8Url, m3u8file, bar='' )
            
            if not ( os.path.getsize(m3u8file) ) > 0:
                print( '    <E> Failed to get m3u8 file. Retry - %s' % m3u8file )
                wget.download( m3u8Url, m3u8file, bar='' )

            self.ksM3u8Files.append( m3u8file )
            prefix = m3u8Url.split('gifshow')[0] + 'gifshow/'
            self.ksM3u8HttpHostPre[m3u8file] = prefix

    ''' get ts Url form local m3u8 file. need to process how to downlaod them. '''
    def KsGetTsUrlFromM3u8File( self ):
        for m3uf in  self.ksM3u8Files:
            prefix  = self.ksM3u8HttpHostPre[ m3uf ]
            videoId = m3uf.split('\\')[-1].split('.')[0]
            tsDir   = self.ksPlaybackUidDir + videoId + '\\'
            if not ( os.path.exists(tsDir) ):
                os.makedirs( tsDir )
            m3ulines = self.Reader( m3uf )
            ts = [ x for x in self.Reader( m3uf) if '.ts' in x ]
            tsUrls = [ prefix + x for x in ts ]
        
            n = 0
            self.downInfos = {}
            for url in tsUrls:
                url  = url.strip('\n')
                name = '%04d' % n
                path =  tsDir + name + '.ts'
                self.downInfos[path] = url   ## { /03.ts : url }
                n = n + 1

            self.KsMutilPhreadDownload()

    ''' download signle main page from uid, save page to local.'''
    def DyDownloadMainPage( self, uid ):
        uid     = uid.strip('\n')
        url     = self.dyUserPageUrl + uid 
        header  = Headers( '', '' )
        req     = urllib.request.Request( url, headers=header.douyin_header )
        htmlContent = urllib.request.urlopen( req ).read()
        utf8Content = str( htmlContent, 'utf-8' ) 
        uidFile = self.dyMyFeedsDir + uid + '.page' 

        if len( utf8Content ) > 0:
            self.Writer( utf8Content, uidFile, 'w+' )
            self.dyMyFeedsMainPageFiles.append( uidFile )
        else:
            print('\t  <E>Error when get mainpage of: %s.'  % uid )
        time.sleep( 1 )

    ''' read uid from file, mutil pthread download main page '''
    def DyDownloadAllMainPageFromUidFile( self ):
        uids = self.Reader(self.dyMyFeedsUidFile)
        pmax = int( self.pmax )
        print('get pmax: %d' % pmax)
        threads = []
        n = 0
        for uid in uids:
            uid = uid.strip('\n')
            num = '%04d' % n
            t = threading.Thread( target=self.DyDownloadMainPage, args=[uid] )
            t.setName( '    <Thread - %s %s >' % (num, uid ) )
            threads.append( t )
            n = n + 1

        for t in threads:
            t.deamon = True
            t.start()
            print( t.getName() )
            while True:
                if len( threading.enumerate() ) < pmax:
                    break
        for t in threads:
            t.join()

    ''' parse main page, get living stream.'''
    def DyGetLiveRoomUrlFromMainPage( self ):
        ##paths = 'C:\\Users\\Administrator\\Desktop\\SUZE004\\out\\dy\\myfeeds\\'
        ##self.dyMyFeedsMainPageFiles= [ paths + x for x in (os.listdir(paths)) ]
        for mainPage in self.dyMyFeedsMainPageFiles:
            pageContent = self.Reader( mainPage)
            pageStringContent = ''.join( pageContent )
            
            liveStatus = re.findall( self.dyLiveStatusReg, pageStringContent)

            if len( liveStatus ) > 0:
                roomUrl = 'https://' + re.findall( self.dyLiveRoomIdReg, pageStringContent )[0]
                roomUrl = roomUrl.replace( '?', '' )
                uidFile = mainPage.replace( '.page', '' )
                self.dyLiveRoomUrls[uidFile]  = roomUrl 
                
    ''' download sigle living main page. save it to local.'''
    def DyDownloadLiveRoomUrlPage( self, url, filename ):
        header = Headers('', '')
        req = urllib.request.Request( url, headers=header.douyin_header )
        htmlContent = urllib.request.urlopen( req ).read()
        filename = filename + '.living' 
        if len( htmlContent ) > 0:
            self.Writer( htmlContent, filename, 'wb' )
            self.dyLiveRoomPageFiles.append( filename )
        else:
            print('    <E>Error when download living room page: %s .' % url )
        time.sleep( 0.5 )

    ''' mutil thread download all living rooms main page'''
    def DyDownloadLivingRoomPageFiles( self ):
        pmax = int( self.pmax )
        print('    <DydownloadLivingRoomPageFiles....... >')
        threads = []
        for uidFile in self.dyLiveRoomUrls.keys():  ## uidFile: url
            url = self.dyLiveRoomUrls[ uidFile ]
            t = threading.Thread( target=self.DyDownloadLiveRoomUrlPage, 
                                  args=[ url, uidFile ] )
            t.setName( '\t\t<Thread -living %s Downloading.... >' % (uidFile.split('\\')[-1]) )
            threads.append( t )
        for t in  threads:
            t.deamon = True
            t.start()
            print( t.getName() )
            while True:
                if len( threading.enumerate() ) < pmax:
                    break
        for t in threads:
            t.join()

    ''' get dy living stream from livingroom mainpage files.'''
    def DyGetLivingSteamUrlFormRoomPageFiles( self ):
        for liveFile in self.dyLiveRoomPageFiles:
            pageContent = self.Reader( liveFile )    
            pageStringContent = ''.join( pageContent )
            title = re.findall( self.dyRoomTitleReg, pageStringContent )[0].split('>')[1].split('<')[0]
            flvs = re.findall( self.dyFlvReg, pageStringContent )
            flvUrl = 'https' + unquote(flvs[0], 'utf-8').split('http')[1]
            self.dyTitleLvingFlvs[title] = flvUrl
            print('\t\t' + title + '   ---->   ' + flvUrl )

         
    ''' parse user intent, choose which should to be done.'''
    def ChooseOperateToDo( self ):
        ''' download short video from input ID or uid File.'''
        if ( self.operate == 'download' ) and ( self.platform=='ks'):
            if ( os.path.isfile(self.data) ) and ( self.dataType=='FILE' ):
                print('  <Download ks short videos from input file: %s... >' % self.data ) 
                userIds = self.Reader( self.data ) 
                for userId in userIds:
                    userId = userId.strip('\n')
                    self.userId = userId
                    self.DownloadPrepare( )
                    print( '\t<Download - %s' % userId )
                    self.jsonFiles = [ ]  ## reset to empty
                    self.KsFetchHttpResponse( userId, '' )
                    self.downInfos = { }  ## reset to empty
                    self.KsGetVideoUrlsFromJsonFile( self.jsonFiles )
                    self.KsMutilPhreadDownload()
                 
            else:
                print('  <Download ks short videos from input ID................. >' ) 
                self.KsFetchHttpResponse( self.userId, self.pcursor )
                self.KsGetVideoUrlsFromJsonFile( self.jsonFiles )
                self.KsMutilPhreadDownload()

        ''' download playback video from ID.'''
        if (self.operate == 'download') and (self.platform=='ksplayback'):
            print('  <Download ksplayback  videos................. >' ) 
            self.KsFetchPlaybackVideoJsonFiles( self.ksPlaybackUid, self.pcursor )
            self.KsGetVieoUrlsFromJsonFiles( )
            self.KsGetM3u8File( )
            self.KsGetTsUrlFromM3u8File( )
        
        ''' get my all ks feeds. '''
        if (self.operate == 'get_myksfeed') and (self.platform=='ks'):
            print('  <Get all ks feeds videos................. >' ) 
            self.KsGetAllFeeds( self.myUserId, self.pcursor )

        ''' get my ks feeds living flv'''
        if (self.operate == 'get_mykslive') and (self.platform == 'ks'):
            print('  <Get all ks living stream flv url ................. >' ) 
            self.KsGetLiveStream( )

        ''' get my dy living stream.'''
        if (self.operate == 'get_mydylive') and (self.platform == 'dy'):
            print('  <Get all dy living stream flv url ................. >' ) 
            self.DyDownloadAllMainPageFromUidFile( )
            self.DyGetLiveRoomUrlFromMainPage( )
            self.DyDownloadLivingRoomPageFiles( )
            self.DyGetLivingSteamUrlFormRoomPageFiles( )
            

    def Run( self ):
        self.DownloadPrepare( )
        self.ChooseOperateToDo( )



