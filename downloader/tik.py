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

header =  {
 'cookie': '''ttwid=1%7COBF4i3Pz7LN3M5daPlQrdpwbSXOHMZCI-1hfUI3zyR8%7C1637812309%7C59bda0ad7b70c9e2bf75c7aeb8bdcd248fc7782ccea15a35c8666e95bab83cd4; ttcid=b85d63c1d42b4d2cb37370d7c67f32dd40; n_mh=Ly5pX1VXcDtRDRGIeDA9LY6F4uZugnXquDwX-6sUs6s; s_v_web_id=verify_l6dccfws_1a6T70YX_nZAt_4XmG_9D8a_Z46JNpPcF2pn; passport_csrf_token=9f54d2e038a19f553f006fb950a2b8f5; passport_csrf_token_default=9f54d2e038a19f553f006fb950a2b8f5; SEARCH_RESULT_LIST_TYPE=%22multi%22; live_can_add_dy_2_desktop=%221%22; douyin.com; strategyABtestKey=1662173395.776; download_guide=%223%2F20220903%22; sso_uid_tt=ba6ed4d8d08df79cd2ba57fcca39debe; sso_uid_tt_ss=ba6ed4d8d08df79cd2ba57fcca39debe; toutiao_sso_user=1c12c008225f7d416ff9e43c95a9621d; toutiao_sso_user_ss=1c12c008225f7d416ff9e43c95a9621d; sid_ucp_sso_v1=1.0.0-KDVkMWFiZjYyNTU1MjlmZTBhOWRhNDk1NDZiYWNlOTA2ZTkwMzk2NGUKHwiX_qCknPWFBBCngsuYBhjvMSAMMPGS8fQFOAZA9AcaAmhsIiAxYzEyYzAwODIyNWY3ZDQxNmZmOWU0M2M5NWE5NjIxZA; ssid_ucp_sso_v1=1.0.0-KDVkMWFiZjYyNTU1MjlmZTBhOWRhNDk1NDZiYWNlOTA2ZTkwMzk2NGUKHwiX_qCknPWFBBCngsuYBhjvMSAMMPGS8fQFOAZA9AcaAmhsIiAxYzEyYzAwODIyNWY3ZDQxNmZmOWU0M2M5NWE5NjIxZA; odin_tt=1eabe7ef8ad528a9d465b113a2b444f476eea3b6f0992d6faca5bfc4df2afca3f48864625a07a2589b316997d87cf7125c124a05d83cc08da4d0b348d17771df; passport_auth_status=9031e1bdbc6e565c3dab5a8146799d60%2C; passport_auth_status_ss=9031e1bdbc6e565c3dab5a8146799d60%2C; sid_guard=5d82165cd775e5071ea5abb57cca9bbd%7C1662173480%7C5183999%7CWed%2C+02-Nov-2022+02%3A51%3A19+GMT; uid_tt=3980bf8c8d30655c7484aadf838b3752; uid_tt_ss=3980bf8c8d30655c7484aadf838b3752; sid_tt=5d82165cd775e5071ea5abb57cca9bbd; sessionid=5d82165cd775e5071ea5abb57cca9bbd; sessionid_ss=5d82165cd775e5071ea5abb57cca9bbd; sid_ucp_v1=1.0.0-KGUwNDZlNjlkMzgwYTNkMDU4ZDM5MmVjY2U4OTk0ZGI4MTY4ZmRkMmQKGQiX_qCknPWFBBCogsuYBhjvMSAMOAZA9AcaAmhsIiA1ZDgyMTY1Y2Q3NzVlNTA3MWVhNWFiYjU3Y2NhOWJiZA; ssid_ucp_v1=1.0.0-KGUwNDZlNjlkMzgwYTNkMDU4ZDM5MmVjY2U4OTk0ZGI4MTY4ZmRkMmQKGQiX_qCknPWFBBCogsuYBhjvMSAMOAZA9AcaAmhsIiA1ZDgyMTY1Y2Q3NzVlNTA3MWVhNWFiYjU3Y2NhOWJiZA; THEME_STAY_TIME=%22299775%22; IS_HIDE_THEME_CHANGE=%221%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz%2F1662220800000%2F0%2F0%2F1662179132852%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz%2F1662220800000%2F0%2F1662178532853%2F0%22; __ac_nonce=06312f8f900595c756e0e; __ac_signature=_02B4Z6wo00f01O2UoVAAAIDBjp5hO6Xk4UTtsKXAAFh99orF-wARPcBy.w1wWnzN6I3QFNNxvfEsoE2BK.S0i1dpUALwDZw2-WoU7rd9B-bq82yGjnfFfu5QdbUVyPPzFHVdJV-fsmqDUK4wc2; home_can_add_dy_2_desktop=%221%22; tt_scid=8bdPuaB7CpzVh7NJnc05lL2n56xBHaxPQYhetEbL2eMcBLzKsWW0KxCUiDYIITfW52b7; msToken=qEZjruDfLrV4alx5HG7uT99yKb2YrtV1KtANXaAz1Il6ecilyzBzHsjfkluOkpSEwBA_3WT-YuqsIXND27ak-uAem1O_f5LKax-Y-K0tjC2L29ySmj1wK3gxRwZBCh9GjA==; msToken=UQV5T94QoQp1LS6rJbUpm8a0UZ_k7d3J9wpIVzGztK4YYnFSiEz9kk-KcP_s2XpL9Syd69vFQGurpbY7x6d4VO194PoY0VdaofhTkpYaIprqHasgYUmAtkDSECeNmcDgYA==''' ,
  'referer':'https://www.douyin.com/user/MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
        }
		
jsons='''device_platform=webapp&aid=6383&channel=channel_pc_web&user_id=2277817727860503&sec_user_id=MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz&offset=40&min_time=0&max_time=0&count=20&source_type=4&gps_access=0&address_book_access=0&is_top=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=104.0.0.0&browser_online=true&engine_name=Blink&engine_version=104.0.0.0&os_name=Windows&os_version=10&cpu_core_num=4&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=100&webid=7034350289385752101&msToken=UQV5T94QoQp1LS6rJbUpm8a0UZ_k7d3J9wpIVzGztK4YYnFSiEz9kk-KcP_s2XpL9Syd69vFQGurpbY7x6d4VO194PoY0VdaofhTkpYaIprqHasgYUmAtkDSECeNmcDgYA==&X-Bogus=DFSzsdVLXK0ANeorSQRVrKXAIQRR'''

url = 'https://www.douyin.com/aweme/v1/web/user/following/list/?' + jsons
##req = urllib.request.Request(url, headers=header)
##req=urllib.request.get(url, headers=header)
##html_content = urllib.request.urlopen(req).read()
r = requests.get(url,headers=header,json=jsons )
rh = r.headers
data=r.text

print('-------Send Header-------------')
reqh = 'msToken'+jsons.split('msToken')[1]
reth = rh['Set-Cookie']
print(reqh)
print('-------Response Header-------------')
print(reth)

with open('./repose','w+', encoding='utf-8') as f:
	f.write(data)

