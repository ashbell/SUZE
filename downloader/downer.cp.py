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


from Headers import  dict_header 
''' header = dict_header(user_id, pcursor)'''

''' 控制直播回放的下载个数，下载前几个，很多作品没内容，或者太久的，不下了'''
BACKCNT = 1

global author_name
global douyin_living

class  user_profile(object):
    def __init__(self, profile_type, user_id, pcursor):
        gifshow_types = ['ks', 'KS', 'gifshow','GIFSHOW']
        gifshow_playback_types = ['ksbk','KSBK','gifshowbk', 'GIFBK']
        if profile_type in gifshow_types:
            print('\tInit Gifshow / user_id: %s   ->  pcursor: %s'  % (user_id, pcursor))
            self.work_dir = './' + 'ks_dir/' + user_id + '/'
            if not os.path.exists(self.work_dir):
                os.makedirs(self.work_dir)
        if profile_type in gifshow_playback_types:
            print('\tInit Gifshow_Playback / userid: %s  -> pcursor: %s'  % (user_id, pcursor))
            self.playbk_dir = './' + 'ks_dir_bk/' + user_id + '/' 
            if not os.path.exists(self.playbk_dir):
                os.makedirs(self.playbk_dir)

    def  move(self):
        pass

    ##@classmethod
    def download_videos(self, video_url='',video_name=''):
        print('\t  downloading.................%s' % video_name )
        """
        bashname = './ksdown.sh'
        cmd = "C:\\cygwin64\\bin\\mintty.exe  -w hide " + " "+ bashname + " " + video_url + " " + video_name
        p = subprocess.Popen(cmd, \
            stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr= subprocess.PIPE)
        shell_out = p.stdout.read()
        shell_error = p.stderr.read()

        ##wget.download(video_url, video_name, bar='')
        """
        cmd = 'wget -O %s %s' % (video_name, video_url)
        ##subprocess.check_output( cmd, text=False )
        ret = subprocess.call(['wget', '-O', video_name, video_url], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        ##print(out.strip('\n'))


    class douyin(object):
        def __init__(self, user_id, pcursor):
            self.user_id = user_id
            print('\tInit.......Douyin...........')

        @classmethod
        def fetch_all_follow_profile(self, user_id, save_path):
            status_info = ''
            header = dict_header(user_id, '')
            ##print(header.douyin_header)
            url = 'https://www.douyin.com/user/' + user_id
            req = urllib.request.Request(url, headers=header.douyin_header)
            html_content = urllib.request.urlopen(req).read()
            utf8_content = str(html_content, 'utf-8') 
            print('\tFetch all follower profile............%d  %s' % (len(utf8_content), user_id))

            live_status_reg = '>直播中<'
            live_status = re.findall(live_status_reg,utf8_content)
            room_reg = 'live.douyin.com/\d+\?'
            if len(live_status) > 0:
                status = live_status[0] 
                title_reg = '<title .*</title>'
                title = re.findall(title_reg, utf8_content)[0].split('>')[1].split('<')[0]
                room_url = 'https://' + re.findall(room_reg, utf8_content)[0]
                room_url = room_url.replace('?', '')
                length = len(utf8_content)
                
                status_info = '\t%s --> %s' % (title, room_url)
            """

            for element in html_elements:
                if '<title' in element:
                    print(element+'------------------------')
            """
            fw = open(save_path,'wb+')
            fw.write(html_content)
            fw.close()
            time.sleep(2)
            return status_info


    class duxiaoshi(object):
        def __init__(self, user_id, pcursor):
            self.user_id = user_id
            print('\tInit.......duxiaoshi...........')
        @classmethod
        def fetch_http_response(self, user_id):
            page_count = 0
            has_more = '1'
            n = 0
            
            while has_more != 0:
                ''' For 13 bit ''' 
                date = datetime.datetime.now()
                unix_time = round(datetime.datetime.timestamp(date)*1000)
                
                ''' For 14 bit '''
                millis = int(round(time.time() *10000))
                c_time = str(millis)
                 
                
                header =dict_header(user_id,'')
                if page_count == 0:
                    header_data = '''tab=main&num=10&uk='''+ user_id+'''&source=pc&type=newhome&action=dynamic&format=jsonp&otherext=h5_20220629154551&Tenger-Mhor=3393969964&callback=__jsonp'''+ str(n) + str(unix_time)
                    ##print(header_data)
                else:
                    header_data = '''tab=shipin&num=9&uk='''+ user_id+'''&source=pc&ctime=''' + c_time+'''&type=newhome&action=dynamic&format=jsonp&otherext=h5_20220629154551&Tenger-Mhor=3393969964&callback=__jsonp'''+ str(n) + str(unix_time)
                    ##print(header_data)
                    
                header_data = '''tab=shipin&num=9&uk=mvLxGAGYbImgsWJQiNdTBQ&source=pc&ctime=16379357188410&type=newhome&action=dynamic&format=jsonp&otherext=h5_20220629154551&Tenger-Mhor=3393969964&callback=__jsonp141656951983149'''
                print(header_data)
                
                url = 'https://mbd.baidu.com/webpage?' + header_data
                req = urllib.request.Request(url, headers=header.duxiaoshi_header)
                html_content = urllib.request.urlopen(req).read()
                ##print(html_content)
                page_count = page_count + 1
                n = n + 2
                name = "%04d" % page_count
                file_name = './baidu/data_' + name
                fw = open(file_name, 'wb+')
                fw.write(html_content)
                fw.close()

                time.sleep(2)
          
        @classmethod
        def analy(self, user_id):
            user_dir = './baidu/'+user_id + '/'
            video_dir = user_dir + 'video/'
            html_dir = user_dir + 'html/'
            html_files =  []
            script_reg = 'window._page_data = .*\"\"\}\};' 
            urls = []
            info = ''
            download_infos = {}

            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            files = os.listdir(html_dir)
            for html in files:
                html_files.append(html_dir+html)
            for html in html_files:
                fr = open(html, 'r', encoding='utf-8')
                lines = fr.readlines()
                fr.close()
                ##print(html)

                
                for line in lines:
                    ##print('-----------------------------------------------')
                    ##print(line)
                    script = re.findall(script_reg, line)
                    if len(script) > 0:
                        json_data = script[0].replace('window._page_data = ', '').replace('""}};','""}}')
                        data = json.loads(json_data)
                        ##meta = type(data['meta']['videoInfo']['clarityUrl'])
                        ##meta = data['meta']['videoInfo']['clarityUrl'][0]['url']
                        try:
                            clarity = data['meta']['videoInfo']['calrityUrl_v2']
                            ##print('--only  clarity v1---------------------------------------------')
                        except:
                            ##print('--only  clarity v2---------------------------------------------')
                            clarity = data['meta']['videoInfo']['clarityUrl']
                            
                        for item in clarity:
                            ##print(item)
                            ##print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
                            info = item
                            if '超清' in item.values():
                                info = item
                            if '蓝光' in item.values():
                                info = item
                        urls.append(info['url'])
                
            for url in urls:
                file_name = url.split('/')[-1]
                video_path = video_dir + file_name
                download_infos[video_path] = url 
            return download_infos
                    
                                
    class  gifshow(object):
        class header(object):
            def __init__(self, user_id, pcursor):
                self.user_id = user_id
                self.pcursor = pcursor
        
        @classmethod
        def get_myfols(self, user_id,pcursor):
            print('\t  Get my fols.....................')
            user_dir = './' + 'fols/' + user_id + '/'
            page_count = 0
            myfols = []
            fols_file = user_dir + 'myflos'
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            while pcursor != 'no_more' :
                print('\t\tGet my_fols @ pcursor: %s' % pcursor)
                old_pcursor = pcursor
                header = dict_header(user_id, pcursor)
                r = requests.post('https://www.kuaishou.com/graphql', headers = header.myfols_header, json=header.myfols_header_json)
                r.encoding='utf-8'
                data=r.text
                if len(data) > 0:
                    page_count =page_count + 1
                    str_page_count = "%04d" % page_count
                    json_file = user_dir + str_page_count +'.json'
                    fw = open(json_file, 'w+', encoding='utf-8')
                    fw.write(data)
                    fw.close()
                json_data = json.loads(data)
                try:
                    pcursor = json_data['data']['visionProfileUserList']['pcursor']
                except:
                    print('\t\tFailed to Get pcursor.....')
                    pcursor = old_pcursor

                try:
                    fols = json_data['data']['visionProfileUserList']['fols']
                    len_fols = len(fols)
                    for num in range(0,len_fols):
                        fols_name = json_data['data']['visionProfileUserList']['fols'][num]['user_id']
                        fols_id = json_data['data']['visionProfileUserList']['fols'][num]['user_name']
                        fols_info = fols_name + '  >  ' + fols_id
                        myfols.append(fols_info)
                except:
                    print('\t\tFaild to Get fols_name or  fols_id')
                time.sleep(2)


            fw =open(fols_file, 'w+', encoding='utf-8') 
            for info in myfols:
                info = info.strip('\n')
                fw.write(info)
                fw.write('\n')
            fw.close()
            time.sleep(2)

        @classmethod
        def  fetch_myfollow_live(self, user_id):
            live_dir = './'+'live/'+user_id + '/'
            if not os.path.exists(live_dir):
                os.makedirs(live_dir)
            download_infos = {}
            header = dict_header(user_id, '')
            url = 'https://live.kuaishou.com/rest/wd/live/liveStream/myfollow'
            req = urllib.request.Request(url, headers=header.myfollow_live_header)
            html_content = urllib.request.urlopen(req).read()
            html_file = live_dir + 'live'
            fw = open(html_file,'wb+')
            fw.write(html_content)
            fw.close()

            json_data = json.loads(html_content)
            data = json_data['follow']
            count = len(data)
            for num in range(0,count):
                nick_name = data[num]['user']['user_name']
                live_url = data[num]['playUrls'][0]['url']
                mills_time = data[num]['startTime']
                ##follow_id = data[num]['user']['principalId']
                eid = data[num]['user']['eid']
                string_time = time.strftime('%Y-%m-%d_%H_%M_%S', time.localtime(mills_time/1000))
                user_stream_dir = live_dir + eid + '/'
                if not os.path.exists(user_stream_dir):
                    os.makedirs(user_stream_dir)
                '''
                if '/' in nick_name:
                    nick_name = nick_name.replace('/','_')
                '''
                nick_file  = user_stream_dir + 'nick'

                fw = open(nick_file, 'w+', encoding='utf-8')
                fw.write(nick_name)
                fw.close()

                flv_path = user_stream_dir + string_time +'.flv'

                download_infos[flv_path] = '%-180s  > %s' % (live_url , nick_name)
                ##print('%s------>  %s  --   %s ' % (nick_file, flv_path, live_url))

            ##print(html_content)
            return download_infos

        @classmethod
        def  list_fetch_https_response(self, user_id, pcursor):
            if len(sys.argv) > 1:
                limit = int(sys.argv[1])/20 + 1
            page_count = 0
            list_json_file = []
            failed = 0
            second = 0
            while pcursor != 'no_more':
                print('\t  list_fetch_https_response: %s \t %s\t :%d seconds' % (user_id, pcursor, second))
                header = dict_header(user_id, pcursor)
                old_pcursor = pcursor
                r = requests.post('https://www.kuaishou.com/graphql', headers = header.common_header, json = header.user_product_json)

                r.encoding = 'utf-8'
                data = r.text
                if len(data) != 0:
                    page_count = page_count + 1
                    str_page_count = "%04d" % page_count
                    user_dir = './' + 'ks_dir/' + user_id + '/'
                    json_file_name = user_dir + str_page_count + '.json'
                    fw = open(json_file_name, 'w+',encoding='utf-8')
                    fw.write(data)
                    fw.close()
                    list_json_file.append(json_file_name)
                else:
                    print('\t error when read data from webserver.')
                    exit()
                
                json_data = json.loads(data)
                try:
                    pcursor = json_data['data']['visionProfilePhotoList']['pcursor']
                except:
                    print('Failed to parse pcursor')
                    pcursor = old_pcursor
                    failed = failed + 1
                if failed > 5:
                    print('Failed to Get pcurosr too many times,  eixt!')
                    exit()

                if len(sys.argv) > 1:
                    if page_count > limit:
                        print('\t\tLimit pages.................................')
                        break
                second = random.randint(5,10) +random.randint(0,5)
                time.sleep(second)
            return list_json_file


        @classmethod
        def  dict_get_video_urls(self, json_files = [], user_id=''):
            print('\n')
            video_count = 0
            video_url = ''
            dict_video_infos = {}
            for jsfile in json_files:
                print('\t  list_get_gifshow_video_infos: %s \t ' % jsfile)
                f = open(jsfile, 'r', encoding='utf-8')
                data = json.load(f)
                f.close()
                global author_name
                try:
                    author_name = data['data']['visionProfilePhotoList']['feeds'][0]['author']['name']
                except:
                    print('Failed to get author name')
                try:
                    video_cnt_page = len(data['data']['visionProfilePhotoList']['feeds'])
                except:
                    print('Failed to get video count in page: %s' % json)
                for id in range(video_cnt_page):
                    video_title = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['caption']
                    if len(video_title) == 0:
                        video_title = 'null_title'
                    try:
                        video_url = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource']['hevc']['adaptationSet'][0]['representation'][0]['url']
                        video_id = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource']['hevc']['videoId']
                    except:
                        video_url = data['data']['visionProfilePhotoList']['feeds'][id]['photo']['videoResource']['h264']['adaptationSet'][0]['representation'][0]['url']
                        video_count = video_count + 1
                        video_id = "%04d" % video_count

                    if (video_url != '') and (video_id != ''):
                        dict_video_infos[video_id] = video_url

            return dict_video_infos
        
        @classmethod
        def str_get_author_name(self, user_id):
            global author_name
            author_name ='yt'
            file =  './' + 'ks_dir/' + user_id + '/' + 'author'
            fw = open(file, 'w+', encoding='utf-8')
            fw.write(author_name)
            fw.close()
            return author_name
           
        @classmethod
        def dict_get_download_infos(self, user_id='', dict_video_infos={}):
            dict_download_infos = {}
            print('\t  dict_get_gifshow_dowload_infos!')
            count = 0
            url_file  = './' + 'ks_dir/' + user_id + '/' + 'video_url'
            video_dir  = './' + 'ks_dir/' + user_id + '/' + 'video/'
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)

            fw = open(url_file, 'w+', encoding='utf-8')
            for video_id in dict_video_infos.keys():
                ##count = count + 1
                ##str_count = "%04d" % count
                fw.write(dict_video_infos[video_id] + '\n')
                video_name = video_dir + video_id + '.mp4'
                dict_download_infos[video_name] = dict_video_infos[video_id] 
            fw.close()
            return dict_download_infos

        @classmethod
        def  logs(self, user_id='', download_infos={}):
            print('\t  gifshow_log:\t'  +  user_id)
            fw = './'
            user_log  = './' + 'ks_dir/' + user_id + '/' + 'log'
            fw = open(user_log, 'w+', encoding='utf-8')
            for name in download_infos.keys():
                info = download_infos[name] + '\t>  ' +  name
                info = info.strip('\n')
                fw.write(info+'\n')
            fw.close()
        @classmethod
        def  diff(self, user_id='' ):
            user_dir = './' + 'ks_dir/' + user_id + '/'
            user_log = user_dir + 'log'
            user_video_dir = user_dir + 'video/'
            
            if os.path.exists(user_log):
                print('find.........old dir, will diff')
                ## make somthing old to diffa
               
    class gifshow_playback(object):
        def __init__(self):
            print('INIT_________________')

        @classmethod
        def list_fetch_video_play_url(self, user_id, pcursor):
            user_dir = './' + 'ks_dir_bk/' + user_id + '/'
            page_count = 0
            play_back_count = 0
            list_json_files = []
            video_play_urls = []
            while pcursor != 'no_more':
                print('\t    list_fetch_video_id: %s \t %s'%(user_id, pcursor))
                header = dict_header(user_id, pcursor)
                old_pcursor = pcursor
                r = requests.post( 'https://live.kuaishou.com/live_graphql', headers=header.playback_header, \
                                    json=header.playback_json )
                r.encoding = 'utf-8'
                data = r.text
                if len(data) > 0:
                    page_count = page_count + 1
                    str_page_count = "%04d" % page_count
                    json_file = user_dir + str_page_count + '.json'
                    fw = open(json_file, 'w+', encoding='utf-8')
                    fw.write(data)
                    fw.close()
                    list_json_files.append(json_file)
                else:
                    print('\t error when read data from webserver')
                    exit()

                json_data = json.loads(data)
                old_pcursor = pcursor
                try:
                    pcursor = json_data['data']['playbackFeeds']['pcursor']
                except:
                    print('\t  error when get pcursor')
                    pcursor = old_pcursor
                time.sleep(3)

            for file in list_json_files:
                fr = open(file, 'r', encoding='utf-8')
                json_data = json.load(fr)
                fr.close()
                ##page_count = len(json)
                try:
                    length = len(json_data['data']['playbackFeeds']['list'])
                except:
                    print('\t error when read product id list lenght')
                    pass
                for num in range(0, length):
                    try:
                        video_id = json_data['data']['playbackFeeds']['list'][num]['productId']
                    except:
                        print('\t error when read product id ')
                        pass
                    if video_id != '' and play_back_count < BACKCNT:
                        video_play_urls.append('https://live.kuaishou.com/playback/'+video_id)
                        play_back_count = play_back_count + 1
            
            return video_play_urls
        
        @classmethod
        def list_fetch_m3u8(self, user_id='', url=''):
            print('\t    list_fetch_m3u8..............................')
            m3u8_reg = 'm3u8Url.*__typename'
            header = dict_header(user_id, '')
            user_dir = './' + 'ks_dir_bk/' + user_id + '/'
            video_id = url.split('/')[-1]
            video_dir = user_dir + video_id + '/'
            video_infos = []
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            html_file  = video_dir + 'html'
            m3u8_file = video_dir + 'm3u8'

            req = urllib.request.Request(url, headers=header.playback_m3u8_header)
            html_content = urllib.request.urlopen(req).read()
            ##data = html_content.decode('UTF-8')
            ##data = html_content.decode("unicode-escape")  
            ''' convert unicode to string, but chinese is fuck!  '''
            ''' utf8 = codecs.decode(html_content, 'utf-8')  convert to Chinese  '''

            fw = open(html_file, 'wb+')
            fw.write(html_content)
            fw.close()

            time.sleep(1)
            data = html_content.decode("unicode-escape")  
            m3u8 = re.findall(m3u8_reg, data)
            m3u8_url = 'https:' + m3u8[0].split(',')[0].split(':')[2].replace('\"','')
            ##print(m3u8_url)
            
            video_infos.append(m3u8_file)
            video_infos.append(m3u8_url)
            
            if os.path.exists(m3u8_file):
                os.remove(m3u8_file)
            wget.download(m3u8_url, m3u8_file,bar='')
            
            if os.path.getsize(m3u8_file) > 0:
                pass
            else:
                video_infos = []
            return video_infos


        @classmethod
        def dict_fetch_ts_file(self, user_id='', video_infos=[]):
            print('\t    list_fetch_ts_file...................')
            m3u8_file = video_infos[0]
            m3u8_url  = video_infos[1]
            ts_dir = m3u8_file.replace('m3u8','ts') + '/'
            download_infos = {}
            if not os.path.exists(ts_dir):
                os.makedirs(ts_dir)
            fr = open(m3u8_file, 'r', encoding='utf-8') 
            lines = fr.readlines()
            fr.close()

            ts_url_prefix = m3u8_url.split('gifshow')[0] + 'gifshow/'
            ts_count = 0

            for ts in lines:
                ts = ts.strip('\n')
                if '.ts' in ts:
                    ts_count = ts_count + 1
                    ts_name = "%04d" % ts_count
                    ts_file = ts_dir + ts_name + '.ts'
                    ts_url = ts_url_prefix +ts
                    download_infos[ts_url] = ts_file
            return download_infos

            
            
        @classmethod
        def ff(self, user_id):
            print('INCCCCfffffffffffffffCCCCCCCCCCCCC ' + user_id)
            
            
        @classmethod
        def gg(self, user_id):
            print('INCCCCCggggggggggCCCCCCCCCCCC ' + user_id)

    """
		def list_get_m3u8_from_video_id( self,  video_id='' ):
			pass
		def list_get_gifshow_playback_ts_url( m3u8_file = '' ):
			pass
			
	class gifshow_live_downloader:
		def bool_live_status( self, user_id='' ):
			pass
		def dict_gifshow_live_header( self ):
			pass
		def dict_gifshow_live_header_json( self ):
			pass
		def list_fetch_gifshow_live_info( self, user_id )
			pass
		def str_get_live_flv_url( live_infos = [] ):
			pass
    """
def douyin_live(user_id):
    profile = user_profile('dy',user_id, '')
    douyin_dir = './douyin/'
    sec_uid_dir = douyin_dir + 'sec_uid/'
    if not os.path.exists(sec_uid_dir):
        os.makedirs(sec_uid_dir)
    uid_file = sec_uid_dir + 'unique_follow_sec_uid'

    fr = open(uid_file, 'r', encoding='utf-8')
    lines = fr.readlines()
    fr.close()
    
    html_dir = douyin_dir + 'html/'
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    class MyThread(Thread):
        def __init__(self, uid, save_path):
            Thread.__init__(self)
            self.uid = uid
            self.save_path = save_path
            self.result = ''
        
        '''
        def run(self, uid, save_path):
            ##self.result = profile.douyin.fetch_all_follow_profile(uid, save_path)
            print('HAHAHAHAHAHHA')
        '''
        def run(self):
            self.result = profile.douyin.fetch_all_follow_profile(self.uid, self.save_path)
            
        def get_result(self):
            return self.result
    
    threads = []
    lock = Lock()

    for uid in lines:
        uid = uid.strip('\n')
        save_path = html_dir  +  uid
        ##print('\tFetch all follw:\t%s ..............' % uid)
        #profile.douyin.fetch_all_follow_profile(uid, save_path)
        ##break

        ##t = threading.Thread(target=profile.douyin.fetch_all_follow_profile, args=[uid, save_path])
        t = MyThread(uid, save_path)
        threads.append(t)

    for t in threads:
        t.daemon = True
        t.start()
        while(True):
            if len(threading.enumerate()) < 20:
                break
    for t in threads:
        t.join()
    
    living_lists = []
    for t in threads:
        result = t.get_result()
        if result != '':
            living_lists.append(result)
    
    header = dict_header(user_id, '')
    print('\t\t ..........Get  %d  living_room......' % len(living_lists))
    for living in living_lists:
        url = living.split('-->')[1].replace(' ','')
        user_info = living.split('-->')[0].replace(' ','')
        req = urllib.request.Request(url, headers=header.douyin_header)
        html_content = urllib.request.urlopen(req).read()
        
        time.sleep(1)
        
        utf8_content = str(html_content, 'utf-8')
        flv_reg  = 'flv_pull_url.*?\.flv'
        flvs = re.findall(flv_reg, utf8_content)

        ''' First is FULL  then is  UHD  SD ...'''
        flv_url = 'https' + unquote(flvs[0], 'utf-8').split('http')[1]
        final_info = '\t %d   %s >> \t %s' %(len(utf8_content), user_info, flv_url)
        print(final_info)


def gifshow_live(user_id):
    profile = user_profile('ks',user_id, '')
    download_infos = profile.gifshow.fetch_myfollow_live(user_id)
    for flv in download_infos.keys():
        print(download_infos[flv])
        ##print(download_infos[flv].split('>')[0].replace(' ', ''))
        ##print(flv)


def duxiaoshi_download(user_id):
    profile = user_profile('bd',user_id,'')
    profile.duxiaoshi(user_id, '')
    ##profile.duxiaoshi.fetch_http_response(user_id)
    down_infos = profile.duxiaoshi.analy(user_id)

    threads = []

    for video_path in down_infos.keys():
        t = threading.Thread(target=profile.download_videos, args=[down_infos[video_path], video_path])
        threads.append(t)
    for t in threads:
        t.daemon = True
        t.start()
        while(True):
            if len(threading.enumerate()) < 8:
                break
    for t in threads:
        t.join()


##duxiaoshi_download('cGJxtbeVYwld3UhvrghIlA')
##duxiaoshi_download('mvLxGAGYbImgsWJQiNdTBQ')

def gifshow_myfols(user_id):
    profile=user_profile('ks', user_id,'')
    profile.gifshow.get_myfols(user_id, '')
    pass

##gifshow_myfols('3xnzffmzps58emw')

class DownloadThread(Thread):
    def __init__(self, url, save_path):
        Thread.__init__(self)
        self.url = url
        self.save_path = save_path
    
    def run(self):
        print('\t\tDownloading...............\t%s' %(self.save_path))
        ##wget.download(self.url, self.save_path)
        cmd = 'wget -O %s --no-check-certificate  %s' % (self.save_path, self.url.replace(' ',''))
        print(cmd)

        return 0
        
        ##os.system(cmd)


def gifshow_product_download(user_id=''):
    profile=user_profile('ks',user_id,'')
    profile.gifshow.header(user_id, '')
    ##profile.gifshow.diff(user_id)
    ##input('>>>>>:')
    list_json = profile.gifshow.list_fetch_https_response(user_id, '')
    list_video_url = profile.gifshow.dict_get_video_urls(list_json, user_id)
    dict_download_infos = profile.gifshow.dict_get_download_infos(user_id, list_video_url)
    profile.gifshow.str_get_author_name(user_id)

    threads = []
    for name in dict_download_infos.keys():
        t = threading.Thread(target=profile.download_videos, args=[dict_download_infos[name],name])
        ##t = DownloadThread(dict_download_infos[name], name)
        threads.append(t)
    profile.gifshow.logs(user_id, dict_download_infos)
    for t in threads:
        t.daemon = True
        t.start()
        while(True):
            if len(threading.enumerate()) < 9:
                break
    for t in threads:
        t.join()

##gifshow_product_download('3xiu8wsuiqraf6w')
##gifshow_product_download('3xbbj3gwpdtn55g')
##gifshow_product_download('3x9ax5yp3qip5sc')
##gifshow_product_download('3x57dennd5q5kg2')
##gifshow_product_download('3xp4i5fa2ruph49')
##gifshow_product_download('3xvy55f3q4v7xhw')
##gifshow_product_download('3xbbj3gwpdtn55g')
##gifshow_product_download('3xqckjfz7zx34uu')
##gifshow_product_download('3xu5cmaccgpbg84')
##gifshow_product_download('3xeqr9c27x6jckk')
##gifshow_product_download('3xn46nuj3v2zcwc')


fl = [
'3xs4sa25thdgmpc',
'3xac42m64kwbdc2',
'3xtcs38hw3spwfs',
'3xz5d5nsx78gkpq',
'3x5b86ebjzp5y2q',
'3xvsu59rdffijii',
'3x8ia3zb25f4c59',
'3x8bt7g9cvew4we',
'3xbhebtp4byw92k',
'3xtgajuyqruxrky',
'3x6vz6qckiku8gq',
'3xpj8nfp2k3mscq',
'3xw8mx2x3249z42',
'3xfbujm7eajbn3u',
'3xf2c8mm5zajk9a',
'3xb8kr5vnyn3uwu',
'3xgw7wrf8gutwrs',
'3x4nsj32icz5u8s',
'3xhzib6uvj8qtzg',
'3xvp8kfvi2s8ce9',
'3xf86cwkrvh4ar9',
'3x7huhspc78i7sm',
'3x2eghgax6cze9c',
'3xxvmk3y6de6866',
'3x83c7zasa3ffyw',
'3xvh836h87yysng',
'3xmyym382ikj2py',
'3xqt7enadyt3z76',
'3xsmbq455v8qk8u',
'3xs9gptrappbx7k',
'3x5edhen4ezhmqs',
'3x4b8d4hny9arx9',
'3xe9b7ww94y9sy9',
'3xkbfsip532nhke' 
]
for lc in fl:
    ##gifshow_product_download(lc)
    pass

def gifshow_playback_download(user_id=''):
    profile=user_profile('ksbk', user_id, '')
    urls = profile.gifshow_playback.list_fetch_video_play_url(user_id, '')
    
    lines = urls
    """
    fr = open('./good.txt','r',encoding='utf-8')
    lines = fr.readlines()
    fr.close()
    """

    for val in lines:
        val = val.strip('\n')
        infos=profile.gifshow_playback.list_fetch_m3u8(user_id, val)
        dict_download_infos = profile.gifshow_playback.dict_fetch_ts_file(user_id, infos)

        threads = []
        for name in dict_download_infos.keys():
            t = threading.Thread(target=profile.download_videos, args=[name,dict_download_infos[name]])
            threads.append(t)
        for t in threads:
            t.daemon = True
            t.start()
            while(True):
                if len(threading.enumerate()) < 5:
                    break
        for t in threads:
            t.join()

    ##profile.gifshow_playback.ff(user_id)
    ##profile.gifshow_playback.gg(user_id)
    ##profile.

##gifshow_playback_download('3xeqr9c27x6jckk')

#

"""

fr = open('./config.ini', 'r', encoding='utf-8')
lines = fr.readlines()
for line in lines:
    config = line.strip('\n')
    if 'download_type' in config:
        op_type = config.split(',')[0].split('=')[1].strip(' ')
        user_id = config.split(',')[1].split('=')[1].strip(' ')
        print(user_id)
        ##gifshow_product_download(user_id)
        ##gifshow_product_download(user_id)
        gifshow_playback_download(user_id)

"""  


fusers = open('./userid', 'r', encoding='utf-8')
users =  fusers.readlines()
fusers.close()

if sys.argv[1] == 'ks':
    gifshow_live('3xnzffmzps58emw')
    
if sys.argv[1].isdigit():
    ##gifshow_product_download('3xxxaynancugad4')
    for gd in users:
        gd = gd.strip('\n')
        gifshow_product_download(gd)
    
if sys.argv[1] == 'dy':
    douyin_live('3cccccc')
    
if sys.argv[1] == 'fl':
    gifshow_myfols('3xnzffmzps58emw')


gifshow_playback_download('3xexe2ywd4ft27a')
