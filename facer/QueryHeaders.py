#!/usr/bin/env   python
# -*- coding: utf-8 -*-

class QueryHeaders( object ):
    def __init__( self, word ):
        self.word = word
        self.header = {
            'Cookie': '''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpf=PC_WEB; kpn=KUAISHOU_VISION; ksliveShowClipTip=true; userId=2183004766; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABV_QrefHXrTBDP-c2-PSf2iDPMMdLCBYPK5w7o9j4lFB4zfQ8fzDMEPlVxG0Rj2RiM3cL4lQfES2Pc91zgi2GtTZNIADgxK0JoCa3FKOXiwCBqYs1a008nkF8qxnr7lC6zWXKS7UsVKSqOha9LIM7zS9o2-RdxjK6q_CkMoygvyVwDnBY9Zv02rIKNu8PqIaYV8y_Z16tmURW_kVpAZCnUxoS9XMBYg26NCtIxdOwhbHEY-u6IiABG33d5yp2LPQeJNEUTVhqxfTTAyJenP_BaBO9Q1KQLigFMAE; kuaishou.server.web_ph=91d19b81dbc91ef07c7f2693850b7cc0b23d''',
            'Host':'www.kuaishou.com',
            'Origin':'https:/www.kuaishou.com',
            'Referer':'https://www.kuaishou.com/search/author?searchKey=' + word,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }
        
        self.queryJson = {
        "operationName":"graphqlSearchUser","variables":{"keyword":word},"query":"query graphqlSearchUser($keyword: String, $pcursor: String, $searchSessionId: String) {\n  visionSearchUser(keyword: $keyword, pcursor: $pcursor, searchSessionId: $searchSessionId) {\n    result\n    users {\n      fansCount\n      photoCount\n      isFollowing\n      user_id\n      headurl\n      user_text\n      user_name\n      verified\n      verifiedDetail {\n        description\n        iconType\n        newVerified\n        musicCompany\n        type\n        __typename\n      }\n      __typename\n    }\n    searchSessionId\n    pcursor\n    __typename\n  }\n}\n"
        }

  
