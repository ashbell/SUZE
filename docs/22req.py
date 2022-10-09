#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import requests
import json
import re
import base64
import subprocess

##regDefi = '{"definition":.*"language_id":0}'
##regDefi = '{"definition":.*?"language_id":0}'
##definition = re.compile(regDefi)
regTitle = 'title.*tag'
regTitleX = re.compile(regTitle)
regAnyvideo = '"anyVideo":{.*}</script>'
regAnyvideoX = re.compile(regAnyvideo)
regVideo = 'dynamic_video_list.*</script>'


""" 构造Http请求头，获得http响应，以text形式返回获取到的内容
"""
def requestResponse( url ):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
        'cookie'    : 'MONITOR_WEB_ID=9fda3470-494f-4c4b-a23a-b64d9c5bdf32;\
            ixigua-a-s = 1; \
            tt_cid = 76680b43602b41d9b1b44bd0209e3af840;\
            __ac_nonce=062761b39006835c82775; \
            __ac_signature=_02B4Z6wo00f01HLyKiwAAIDBEfjqRJabzaBy0i6AAH7S8d5aGZW.xba32DYb8j3Acx \
                       PeypM5ujN395315toeyslG0sL8jGO9UZO-U8hKaXYjrUhU2CQMo2jCd3ePsi9XiiN7QIrYARfO9BpJ5d; \
            BD_REF=1; \
            support_avif = true;\
            msToken = LlPs99DjNgdwHAoHSUlIMqLIzUkaYkRE20AbAL1KiR5_fFngA_mqcsRK93bXWc25M2dfSIcQDPSRVl4gfNtr1Lg\
                      CDx6jc8nETcsO8T6qeM6nY43PB4Gqlw==;\
            passport_csrf_token = 9c5b9a057dfc8848978abaabd5858267;\
            s_v_web_id = verify_33b92b35c275a2a28eb72fd56e2a583b;\
            ttwid = 1%7Cx3P_As7n47XfKV6AdcQik9lE3EIgg6uDmo6fWg6j3Dc%7C1651907406%7C5b0fcd1ffb6fdff843a0412a1421eece8c74937cb5be706dcc070b57dd06a5b3' 
    }

    r = requests.get(url, headers=headers)
    r.encoding='utf-8'
    data = r.text

    return data

""" //////////////////////////////////////////////////////////////////////
"""


""" 根据url获取视频的ID, 作为字典的key值
"""
def getVideoId( url ):
    try:
        videoId = url.split('/')[3]
    except:
        print('@ getVideoId: url有误，请检查!!\n')

    return videoId 
""" //////////////////////////////////////////////////////////////////////
"""

""" 提取音频和视频的Url和属性,返回一个数据表
    videoAttr = { id:[360p>mp4>url1, 480p>mp4>url2, bitrate1>audio,aurl1, bitrate2>audio>arul2]}
"""
def fetchUrls( data ):
    result  = {}
    alls    = []
    match   = re.findall( regVideo, data )
    for item in match:
        sp = item.split('definition')
        for val in sp:
            ausp = val.split('dynamic_audio_list')
            for au in ausp:
                alls.append(au)
    ## 分离出视频，音频，判定依据是 vheight 和vwidth
    videos = []
    audios = []
    for val in alls:
        if 'main_url' in val:
            if ('vwidth' in val) and ('vheight' in val):
                videos.append(val)
            else:
                audios.append(val)
    
    videoAttrs  = ''
    audioAttrs  = ''
    strings     = []
    for val in videos:
        vtype       = ''
        videoUrl    = ''
        splited     = val.split(',')
        for item in splited:
            if 'vtype' in item:
                vtype = item.split(':')[1].strip('\"')
            if 'main_url' in item:
                videoUrl = item.split(':')[1].strip('\"')

        videoAttrs = splited[0].split(':')[1].strip('\"')+ '>' + vtype + '>' + videoUrl
        strings.append(videoAttrs)
        ##print(videoAttrs)
        ##print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

    for val in audios:
        audioType   = ''
        audioUrl    = ''
        bitRate     = ''
        splited     = val.split(',')
        for item in splited:
            if 'vtype' in item:
                audioType = item.split(':')[1].strip('\"')
            if 'main_url' in item:
                audioUrl = item.split(':')[1].strip('\"')
            if 'real_bitrate' in item:
                bitRate =  item.split(':')[1].strip('\"')
        audioAttrs = bitRate + '>' + audioType + '>' + audioUrl
        strings.append(audioAttrs)
        ##print(audioAttrs)
        ##print('vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv')

    result[videoID] = strings
    ##print(result)
    return result


""" //////////////////////////////////////////////////////////////////////
"""


""" 获取url网页中所有的main_url,  返回一个由 ID 和 所有视频/音频属性组成的字典, 数据格式：
    { 123123:[ [360p, type,  url],   [720p, type, url]  ]  }
    参数 data: http 的响应内容
"""
def getVideoAttrs( data ):
    videoAttr = {}
    jsonItem = data.split('{')
    for item in jsonItem:
        resolution = 'None'
        vtype = ''
        base64Url = ''
        attrStr = ''

        if 'main_url' in item:
            ##print(item)
            valueArray = item.split(',')
            for value in valueArray:
                if 'definition' in value:
                    resolution = value
                if 'vtype' in value:
                    vtype = value
                if 'main_url' in value:
                    base64Url = value

            if resolution != 'None': 
                resolution = resolution.split(':')[1].replace('"','')
            else:
                resolution = 'Audio'

            if vtype != '' and base64Url != '': 
                vtype = vtype.split(':')[1].replace('"','')
                base64Url = base64Url.split(':')[1].replace('"','')
                attrStr = resolution + '>' + vtype + '>' + base64Url

            if len(videoAttr) == 0:
                videoAttr[videoID] = [attrStr]
                ##print('first add')
            else:
                ##print('other add=====' + attrStr )
                videoAttr[videoID].append(attrStr)
    ##print(videoAttr)
    return videoAttr
""" //////////////////////////////////////////////////////////////////////
"""

""" 从数据中，找出最高分辨率的视频, videoAttr 为经过格式化处理的数据条目
    result['1080p', audio url]
"""
def getBestVA( videoAttr ):
    """ order[] = [1080p fps, 1080, 720, 480, 360 ]
    """
    bestVideoFlag = ''
    bestAudioUrl = ''
    result = []
    for  item in videoAttr.keys():
        order = [ 0, 0, 0, 0, 0 ]
        for val in videoAttr[item]:
            ##print(val)
            if '360p' in val:
                order[4] = 1
            if '480p' in val:
                order[3] = 2
            if '720p' in val:
                order[2] = 3
            if '1080p' in val:
                order[1] = 4
            if '1080p 60fps' in val:
                order[0] = 5

            if (bestAudioUrl == '') and ('Audio' in val):
                bestAudioUrl = val
                ##print('++++++++++'+bestAudioUrl)
            else:
                pass

        order.sort(reverse=True)
        print(order)
        if   order[0] == 5:
            print('best is 1080p 60fps')
            bestVideoFlag = '1080p 60fps'
        elif order[0] == 4:
            print('best is 1080p')
            bestVideoFlag = '1080p'
        elif order[0] == 3:
            print('best is 720')
            bestVideoFlag = '720p'
        elif order[0] == 2:
            print('best is 480 fps')
            bestVideoFlag = '480p'
        elif order[0] == 1:
            print('best is 360 fps')
            bestVideoFlag = '360p'

    result.append(bestVideoFlag)
    result.append(bestAudioUrl)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    ##print(result)
    ##print('\n')
    return result
        
""" //////////////////////////////////////////////////////////////////////
"""

""" base64 转码功能, 转为西瓜视频的格式，自动加上 /?a=xxx 中的 问号
    注意base64加密长度的问题，要 补一个 = ，否则decode会报错
"""
def base64decode( string ):
    if  (string != '') and ('\\u002F' in string):
        urlStr = string.replace('\\u002F', ']')
        part1 = urlStr.split(']')[0]
        part2 = urlStr.split(']')[1]
        part1 = str(part1) + '='
        part2 = str(part2) 
        
        decodePart1 = base64.b64decode(part1.encode('utf-8')).decode('utf-8')
        decodePart2 = base64.b64decode(part2.encode('utf-8')).decode('utf-8')

        realUrl = decodePart1 + '?' + decodePart2
    else:
        realUrl = base64.b64decode(string.encode('utf-8')).decode('utf-8')

    return realUrl

""" //////////////////////////////////////////////////////////////////////
"""


""" 因为1个1080P的地址有多个，所以需要先确立最高分辨率，再来一个个查找1080P的地址，
    音频选取一个就行了, 有的视频做了音视频分离，就有无水印的，没有做分离的就带水印
"""
def getVAbase64Str(  videoAttr={}, flag=[] ):
    print('In getVAbase64============================================')
    ##print(videoAttr)
    print('---------------')
    ##print(flag)
    audioUrl = ''
    splitedAudio = True 
    if flag[1] != '':
        baseAudio = flag[1].split('>')[2]
        audioUrl = base64decode( baseAudio)
        if 'mp4a' in audioUrl:
            #print('Audio:'+'\t'+audioUrl)
            splitedAudio = True
        else:
            splitedAudio = False
            print('Maybe video is too old, no splited  audio file found!')
    else:
        splitedAudio = False

    vflag = flag[0]
    
    videos = []
    for  item in videoAttr.keys():
        for val in videoAttr[item]:
            if vflag in val:
                videos.append(val)
    uniqueVideoUrl = list(set(videos))

    urls = [] 
    for baseStr in uniqueVideoUrl:
        baseUrl = baseStr.split('>')[2]
        finalUrl = base64decode( baseUrl )
        urls.append(finalUrl)
    if splitedAudio:
        return (splitedAudio, audioUrl, urls)
    else:
        return (splitedAudio, 'None', urls)


def maxBitrate( hasSpaudio, audio='', urls = []):
    ## 如过没有分离的音频，那么取一个最大码率的MP4作为最终的
    splitedAudio = True
    splitedAudio = hasSpaudio
    bestVideoUrl = ''
    bestAudioUrl =''
    if splitedAudio == False:
        maxBr = []
        for item in urls:
            if ('mime_type=video_mp4' in item) \
                and('media-video-avc1' in item):
                ##maxBr.append( item)
                ##FUCK!!!!!!!!
                pass
            else: 
                maxBr.append( item)
        best = []
        print(maxBr)
        for val in maxBr:
            br = val.split('&')
            for div in br:
                if 'br=' in div:
                    best.append( int( div.split('=')[1] )  )

        best.sort(reverse = True)
        print('---------------------')
        print(best)
        bestFlag = 'br='+str(best[0])
        print('\tBest bitrate is:\t'+ bestFlag)
        
        for val in maxBr:
            if bestFlag in val:
                bestVideoUrl = val
                break
        #print('Best brUrl is:\n\t' + bestVideoUrl )
    ## 如果有分离的音频，需要返回音频和视频两个地址
    else:
        bestAudioUrl = audio
        bestVideoUrl = ''
        for item in urls:
            if 'media-video-avc1' in item:
                if 'mime_type=video_mp4' in item:
                    bestVideoUrl = item
                    break

    if bestAudioUrl == '':
        print('Has water Mark BestVideo:\n\t'+bestVideoUrl )
        return ('water', 'none', bestVideoUrl)

    else:
        print('BestAudio:\n\t'+bestAudioUrl )
        print('NO water Mark BestVideo:\n\t'+bestVideoUrl )
        return ('no_water', bestAudioUrl, bestVideoUrl)
        
""" //////////////////////////////////////////////////////////////////////
"""

""" 获取视频的标题
"""
def getTitle( data ):
    originData = data.replace('{"','\n{"')
    title = re.findall(regTitleX, originData)
    if len(title) > 0:
        titleStr = title[0].split('\"')[2]
    return titleStr
""" //////////////////////////////////////////////////////////////////////
"""

""" 获取作者信息
"""
def getAuthorName( data ):
    author = ''
    splitedData = data.split(',')
    for item in splitedData:
        if '\"name\"' in item and '}' in item:
            if not 'script' in item: 
                try:
                    author = item.split(':')[1]
                    author = author.replace('}','')
                    author = author.replace('\"','')
                except:
                    print('Get author name failed!: \t' + item )
    return author
""" //////////////////////////////////////////////////////////////////////
"""
"""  数据处理完毕，开始下载到本地
"""
def downloadVideos( hasWater, audioUrl, videoUrl ):

    print(hasWater)
    print(audioUrl)
    print(videoUrl)
    author = getAuthorName ( data )
    title = getTitle(data)
    storeDir = './'+ author + '/'
    videoDir = storeDir + title
    if not os.path.exists(storeDir):
        os.makedirs( storeDir)

    bashname = './xgdown.sh'

    if 'water' == hasWater:
        videoName = storeDir + 'water_'+ title + '.mp4'
        videoName = videoName.replace(' ','_')
    

        p = subprocess.Popen(["C:\\cygwin64\\bin\\mintty.exe ", bashname, videoUrl, videoName  ], \
                        stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()
    elif 'no_water' == hasWater:
        audioName = storeDir + 'no_water_' + title + '.mp4a'
        videoName = storeDir + 'no_water_' + title + '.mp4'
        videoName = videoName.replace(' ','_')
        audiooName = audioName.replace(' ','_')
        
        p = subprocess.Popen(["C:\\cygwin64\\bin\\mintty.exe ", bashname, videoUrl, videoName  ], \
                        stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()

        p = subprocess.Popen(["C:\\cygwin64\\bin\\mintty.exe ", bashname, audioUrl, audioName  ], \
                        stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()

    else:
        print('unknow options!')

""" //////////////////////////////////////////////////////////////////////
"""
""" 完整的流程走一遍，通过读取url文档，实现多个下载
"""

def allProcess( url ):
    log = open('./log.txt', 'w+', encoding='utf-8')
    data = requestResponse( url )
    author = getAuthorName ( data )
    videoID = '' 
    videoID = getVideoId( url )
    videoAttr = {}
    videoAttr = getVideoAttrs( data )
    flag = []
    flag = getBestVA( videoAttr )
    para = getVAbase64Str( videoAttr, flag )
    print(para)
    para2 = maxBitrate(para[0],para[1],para[2])
    downloadVideos(para2[0], para2[1],para2[2])
    logInfo1 = url + '--' + 'para[0]' +para[1]  + para[2]+'\n'
    logInfo2 = url + '--' + 'para2[0]'+para2[1] + para2[2]+'\n'
    log.write(logInfo1)
    log.write(logInfo2)
    log.close()

""" //////////////////////////////////////////////////////////////////////
"""
f = open('./url.txt', 'r', encoding='utf-8')
urls = f.readlines()
f.close()

for url in urls:
    url = url.strip('\n')
    log = open('./log.txt', 'a+', encoding='utf-8')
    log.write(url+'\n')
    data = requestResponse( url )
    author = getAuthorName ( data )
    global videoID 
    videoID = getVideoId( url )
    fetchUrls( data )
    videoAttr = {}
    videoAttr = getVideoAttrs( data )
    flag = []
    flag = getBestVA( videoAttr )
    para = getVAbase64Str( videoAttr, flag )
    print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    ##print(para)
    para2 = maxBitrate(para[0],para[1],para[2])
    downloadVideos(para2[0], para2[1],para2[2])
    logInfo1 = url + '\t----' + para2[0].strip('\n') +'\n\t'  \
               +para2[1].strip('\n') +'\n\t' + para2[2].strip('\n')+'\n'
    log.write(logInfo1)
    log.close()


 

