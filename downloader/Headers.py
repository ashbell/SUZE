#!/usr/bin/env python
# -*- coding: utf-8 -*-

##class Headers( self,  user_id='' , pcursor='' ):
class Headers(object):
    def __init__(self, user_id, pcursor):
        self.user_id = user_id
        self.pcursor = pcursor
        self.user_info_header_json={
                "operationName":"visionProfile",
                "variables":{"userId":self.user_id},
                "query":"query visionProfile($userId: String) {\n  visionProfile(userId: $userId) {\n    result\n    hostName\n    userProfile {\n      ownerCount {\n        fan\n        photo\n        follow\n        photo_public\n        __typename\n      }\n      profile {\n        gender\n        user_name\n        user_id\n        headurl\n        user_text\n        user_profile_bg_url\n        __typename\n      }\n      isFollowing\n      __typename\n    }\n    __typename\n  }\n}\n"
        }

        self.user_product_json = {
            "operationName": "visionProfilePhotoList",
            "variables": {
                "userId": self.user_id,
                "pcursor": self.pcursor,
                "page": "profile"
            },
            "query": """fragment photoContent on PhotoEntity {\n  id\n  duration\n  caption\n  likeCount\n  viewCount\n  realLikeCount\n  coverUrl\n  photoUrl\n  photoH265Url\n  manifest\n  manifestH265\n  videoResource\n  coverUrls {\n    url\n    __typename\n  }\n  timestamp\n  expTag\n  animatedCoverUrl\n  distance\n  videoRatio\n  liked\n  stereoType\n  profileUserTopPhoto\n  __typename\n}\n\nfragment feedContent on Feed {\n  type\n  author {\n    id\n    name\n    headerUrl\n    following\n    headerUrls {\n      url\n      __typename\n    }\n    __typename\n  }\n  photo {\n    ...photoContent\n    __typename\n  }\n  canAddComment\n  llsid\n  status\n  currentPcursor\n  __typename\n}\n\nquery visionProfilePhotoList($pcursor: String, $userId: String, $page: String, $webPageArea: String) {\n  visionProfilePhotoList(pcursor: $pcursor, userId: $userId, page: $page, webPageArea: $webPageArea) {\n    result\n    llsid\n    webPageArea\n    feeds {\n      ...feedContent\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"""
        }

        self.common_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
            'Cookie': '''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpf=PC_WEB; kpn=KUAISHOU_VISION; ksliveShowClipTip=true; userId=2183004766; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqAB17DLpzUTD_qjv3vyaZKwRcy_f0pkKiAKICOcX5rw_002wqdZ-v-NBulIqekw8RmsA7jB6rfStLJ1zSJfLYiAcmteIvx5do5lhuaClWnAJVV8R9t3kfpUltpSTpYL7qox0f0xFQX-jG94KPX7QlR0xDiYLCY8U4ss3GDXH0fNO-21eEhdV31NaJIhUkGd9XsWU241tqBQZd28X4k05ZoqEhoSKS0sDuL1vMmNDXbwL4KX-qDmIiAJBqZgMMxVmc9cVbq3cCfmApzfmPFImno7IYpiUqvifSgFMAE; kuaishou.server.web_ph=f9c42647af575f0d7b036a1647750da6234b''',
            'Host' :'www.kuaishou.com',
            'Referer':'https://www.kuaishou.com/profile/'+ self.user_id,
            'Upgrade-Insecure-Requests':'1'
        }

        self.playback_header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                'Cookie': '''didv=1639723295303; clientid=3; did=web_c350de8882c38c320f842467ed72e25c; client_key=65890b29; kpn=GAME_ZONE; kuaishou.live.bfb1s=9b8f70844293bed778aade6e0a8f9942; userId=2183004766; userId=2183004766; kuaishou.live.web_st=ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgAS7R5sWnIMiYjGNXC5i0C-U1bZvXR2b3L2tILi0LjCaQJ9VQmCZmRlkWe382iiWg15mWEaoosDx_vT-CMmkBDI3b86lAZYKkH-1OnTk5vBxq9a57mCTP7i3UdUVxTajmpXQKSuW23qDWvnd0_GWx_OH4so_9WH3vSHCWlrZFuggAjoxoHLdaZXL6rkcmF9X74dnRU8A85l9AnwyS_YTxVQEaEhq2DZZ7DUHSmXUzdRyAf3O3USIg326un8BxgjYKdyWPfFl682NSjNw-o6vwkD1rpyTYqUsoBTAB; kuaishou.live.web_ph=56e47702aee94816b57ece4a01052bf43829''',
                'Host':'live.kuaishou.com',
                'Origin':'https://live.kuaishou.com',
                'Referer':'https://live.kuaishou.com/profile/'+ self.user_id


        }
        self.playback_json = {
                "operationName":"playbackFeedsQuery","variables":{"principalId":self.user_id,"pcursor":self.pcursor,"count":24},"query":"query playbackFeedsQuery($principalId: String, $pcursor: String, $count: Int) {\n  playbackFeeds(principalId: $principalId, pcursor: $pcursor, count: $count) {\n    pcursor\n    list {\n      baseUrl\n      caption\n      commentCount\n      coverUrl\n      createTime\n      duration\n      likeCount\n      likeStatus\n      manifestUrl\n      productId\n      viewCount\n      __typename\n    }\n    __typename\n  }\n}\n"
        }

        self.playback_m3u8_header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
            'Cookie':'''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpn=GAME_ZONE; ksliveShowClipTip=true; userId=2183004766; userId=2183004766; kuaishou.live.bfb1s=9b8f70844293bed778aade6e0a8f9942; kuaishou.live.web_st=ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgAZKlpAAD3QFST5I_dRrWecJPNTYP-QePWE5gnLnGWbskQynLUdTeGEo97zL2gWTWQjEf627_Mt_uhXEr3DyU4y_CJ8EaWgeaTzUU4Kv_5m7LsBOUjHwOkcmDM99lOWeFReTtcmkvnTvQCmVzaGSo81O48LXOYpusFPyvM2i_F2ThrwoIOqyIBeBKNpdCw-tIM_dR_OnRRxjbyix3yxEQ4l8aEoMRdS355EPfvO-WEFcOv_Ls2yIgWtbKsUZTjW-MWyA9JNTs6YqwG-z_UQyTqp7EUOB8lpMoBTAB; kuaishou.live.web_ph=2bd5ff77f432d3b83106f56a58e8055a2ade''',
            'Host':'live.kuaishou.com',
            'Referer':'https://live.kuaishou.com/profile/' + self.user_id 
        }

        self.myfollow_live_header = {
            'Cookie': '''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpn=GAME_ZONE; ksliveShowClipTip=true; userId=2183004766; kuaishou.live.bfb1s=3e261140b0cf7444a0ba411c6f227d88; userId=2183004766; kuaishou.live.web_st=ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgAQSZYAGYuh7ctbuHueQGofk6MF3cXCqH_M4hcX17IZUYKiClAY_dRxJd2y1WAYAOMuoJgYBrKQil2ZN3Jj9C3mMJaiDStx0HofD1ueGarcblPfbD1_nZnrDIaKPsMOsnIccaKLD_-4TsYu6-hT1mbKUXdh9KkQZaVt9t2qHfdJ7IsHGzRxS_PoZsAFWQZDKVrAZjlRSEHEESYVd1kN49rzsaEsvpGUru20c-iIt7T0W8MQrXwiIgegfm7s8YcWGBrX9OW_A5qksSWg6826lfCwBT28hD3h0oBTAB; kuaishou.live.web_ph=f5d281ee8a437db96b1841d286dd37f02b07''',
            'Host': 'live.kuaishou.com',
            'Referer': 'https://live.kuaishou.com/u/3xeqr9c27x6jckk',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }

        self.myfols_header = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
                'Cookie':'''clientid=3; did=web_df3ecd2eb6a0128616ec78bf6841449a; client_key=65890b29; kpf=PC_WEB; kpn=KUAISHOU_VISION; ksliveShowClipTip=true; userId=2183004766; kuaishou.server.web_st=ChZrdWFpc2hvdS5zZXJ2ZXIud2ViLnN0EqABA8u_9kPGIpBUYy7ZKtga5RR7NJK6LPYPG9Wn45b7ojNNW6M-jIKAz05SpXbMCSElse8TDIHtUT9m12kEzOOto2fDWfmTM0rGQKo7AECQO6BhWdBHc9twL9_fdQTBNvR4CINndPsSVISEgIEnu6sK_PR14N2psUYn8Rh5BhmtGdKfSMchOzsdctRzU-15C4ioLg2Lo6fWFTm3d1yQQt8BwhoS1KQylfZfbCBEuMI0IcjfqenKIiB9wXaBqa2cNXzKyy2wSRiclmhQTdfiImlZBiUbQJC0_CgFMAE; kuaishou.server.web_ph=89df89c0b2917ee55e2f72a7f0119acd1c63''',
                'Host':'www.kuaishou.com',
                'Origin':'https://www.kuaishou.com',
                'Referer':'https://www.kuaishou.com/profile/' + self.user_id
        }

        self.douyin_header = {
                'cookie': '''ttcid=a20145037093491b9379022bec274f4517; ttwid=1%7CI0VQlKIHEBIxbRGPyc85kBtXB1n1AiaJZbskC0oCXZE%7C1646915015%7C9128a75be17ea24e748ed750176678d2dddba4561462662a7bb45566a2891c01; n_mh=Ly5pX1VXcDtRDRGIeDA9LY6F4uZugnXquDwX-6sUs6s; passport_csrf_token=634d91014d4cce4960e83ab077d256c9; passport_csrf_token_default=634d91014d4cce4960e83ab077d256c9; sso_uid_tt=4e3c83c74b4ec7cd4e4b08b56d924a5b; sso_uid_tt_ss=4e3c83c74b4ec7cd4e4b08b56d924a5b; toutiao_sso_user=876c449be363cc6a703ef4b40d14664a; toutiao_sso_user_ss=876c449be363cc6a703ef4b40d14664a; sid_ucp_sso_v1=1.0.0-KGY3ZTUwNGE3YmYxMGJmNmJhODg3ZjJmN2ZmNGRiOGU5YWU0ODBiNWQKHwiX_qCknPWFBBCFls-WBhjvMSAMMPGS8fQFOAZA9AcaAmxmIiA4NzZjNDQ5YmUzNjNjYzZhNzAzZWY0YjQwZDE0NjY0YQ; ssid_ucp_sso_v1=1.0.0-KGY3ZTUwNGE3YmYxMGJmNmJhODg3ZjJmN2ZmNGRiOGU5YWU0ODBiNWQKHwiX_qCknPWFBBCFls-WBhjvMSAMMPGS8fQFOAZA9AcaAmxmIiA4NzZjNDQ5YmUzNjNjYzZhNzAzZWY0YjQwZDE0NjY0YQ; odin_tt=6db7b9de8c9f91b4e110492eb133b416023ccabc6637beb359eaf0e1a479e4e5a6e8caa5bd9a56b67b0660bc796595dcdddcb0fd3ec8e2e3f946a100f1081e96; sid_guard=876c449be363cc6a703ef4b40d14664a%7C1658047239%7C5184000%7CThu%2C+15-Sep-2022+08%3A40%3A39+GMT; uid_tt=4e3c83c74b4ec7cd4e4b08b56d924a5b; uid_tt_ss=4e3c83c74b4ec7cd4e4b08b56d924a5b; sid_tt=876c449be363cc6a703ef4b40d14664a; sessionid=876c449be363cc6a703ef4b40d14664a; sessionid_ss=876c449be363cc6a703ef4b40d14664a; sid_ucp_v1=1.0.0-KDA2YWRlN2FmYjhmZGYyMDRlOWQ0NWQ0MjlhOGMwMjA1MmJjOGE4ZjgKHwiX_qCknPWFBBCHls-WBhjvMSAMMPGS8fQFOAZA9AcaAmxmIiA4NzZjNDQ5YmUzNjNjYzZhNzAzZWY0YjQwZDE0NjY0YQ; ssid_ucp_v1=1.0.0-KDA2YWRlN2FmYjhmZGYyMDRlOWQ0NWQ0MjlhOGMwMjA1MmJjOGE4ZjgKHwiX_qCknPWFBBCHls-WBhjvMSAMMPGS8fQFOAZA9AcaAmxmIiA4NzZjNDQ5YmUzNjNjYzZhNzAzZWY0YjQwZDE0NjY0YQ; s_v_web_id=verify_l74wpab8_npQ63hEs_OU8L_4kwL_BK1N_tX5JMlXHbzP4; THEME_STAY_TIME=%22299606%22; IS_HIDE_THEME_CHANGE=%221%22; live_can_add_dy_2_desktop=%221%22; download_guide=%223%2F20220831%22; __ac_nonce=0631434870064d5ff2d1d; __ac_signature=_02B4Z6wo00f019r0OFQAAIDC8X5jkdkK1tPa0DzAAJWyIzENoyCe1lgK.yPl5i.AidzPZqIZpUje7n67tJ6GpsDxQ3f9JapLPeQP27rPbjEtcifHJDzZPDmF5OKC5vQQJ3S8BRHQoFp7Pv9qea; douyin.com; strategyABtestKey=1662268553.032; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAA0yFG5TY4LgzgR6MHXJQlieD6BPQxpY37MHlUGhBEeQHN2PsHmf0uI_5IjKb3g3bz%2F1662307200000%2F0%2F1662268553445%2F0%22; home_can_add_dy_2_desktop=%221%22; msToken=MQM_eUz_FLHSfW0vwlCErDUQScV8u60soeRnknCL73_Yn2HlD6-N5WM66XUk9aZkEjsI9vTHC5K--13p4jPlmO4UVuO3j_honKwZ2PS6i7WiV7K9LO-sNN1cWBA1KObBtg==; msToken=OYB9XOPXjfMzAa25H8U72ZGdiS2gRkHwmMdh8_IiBSDWE2Xi6nyfgrjMFlcp1UvlPh_dwwWgnGBdho4DYwMDCfjO0CRO6k9XQm_3rnFUH0WHCB5ePP-7ylSY30tTLIdVKQ==; tt_scid=DG.24yCOlZehy6KwHgBGKNU6Jp-RGL9CF2NNsGrrs96XzQUUtTTvyYwIb2YjdEmxda1a''',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

        }
        self.myfols_header_json = { 
                "operationName":"visionProfileUserList","variables":{"ftype":1, "pcursor":self.pcursor},"query":"query visionProfileUserList($pcursor: String, $ftype: Int) {\n  visionProfileUserList(pcursor: $pcursor, ftype: $ftype) {\n    result\n    fols {\n      user_name\n      headurl\n      user_text\n      isFollowing\n      user_id\n      __typename\n    }\n    hostName\n    pcursor\n    __typename\n  }\n}\n"
        }

        self.duxiaoshi_header = {
                'Cookie': '''BIDUPSID=BDEA8421270036C92C53BB7C4E42DFD6; PSTM=1646844553; BAIDUID=BDEA8421270036C9458FBFDA988C5181:FG=1; H_WISE_SIDS=110085_127969_131862_179347_184716_189755_190627_191067_191250_192958_194085_194512_195343_196425_196527_197241_197711_197956_198261_199022_199575_200596_200993_201104_201193_201546_201699_202545_202651_203309_203317_203361_203525_203605_204032_204122_204254_204305_204535_204545_204701_204779_204864_204911_204954_205218_205239_205412_205484_205548_205844_205958_206007_206124_206197_206252_206277_206288_206516_206681_206870_206905_207003_207021_207025_207144_207212_207237_207307_207364_207498_207552_207565_207609_207610_207715_207729_207830_207885_208054_208093_208112_208165_208225_208268_208271; BDUSS=XFYTWRuYTFzcmFkR2dFSTdBbEE5MmRUZ2pOY25ZMjE4QnNTN0k4MmFWcHNtWHBpRVFBQUFBJCQAAAAAAQAAAAEAAAAxj2QuxKe-~TE2OQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGwMU2JsDFNie; BDUSS_BFESS=XFYTWRuYTFzcmFkR2dFSTdBbEE5MmRUZ2pOY25ZMjE4QnNTN0k4MmFWcHNtWHBpRVFBQUFBJCQAAAAAAQAAAAEAAAAxj2QuxKe-~TE2OQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGwMU2JsDFNie; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BA_HECTOR=a50l8k0ka5aha4200l1hc5lec14; BAIDUID_BFESS=BDEA8421270036C9458FBFDA988C5181:FG=1; ZFY=ZYPfTSqy6xUy24oFLi6d:B7OXFdoeM7uCQo:BMirm:Bpgc:C; Hmery-Time=3393969964; ab_sr=1.0.1_MmZlN2QwYTBmYzU4MWFmNjM2MmNjYmMyOTBlN2YzNDliYzIxMGYyNjA4MzhhNTEwZWEyYzk1ZjIzMTFlOGUwOGMzNWM3YTEyNDZjZmEyYWQ2ZTBiNDQ3N2YyZDFhZWZiNWQwNzMwOTY4MTZlODZmOTg0MzRjNDA4NGVkMmM2OTVmN2ExMDg2NTk3YjQ0MWI2ZWMxZTc4NzI0MDdlMjJmMQ==''',
        'Host': 'mbd.baidu.com',
        'Referer': 'https://author.baidu.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
        }



	
