#!/usr/bin/env   python
# -*- coding: utf-8 -*-
import os
import sys
import argparse

''' 自动上传到百度网盘, 自动寻找已经压缩好的目录，上传文件，./bdupload.py  path '''
## os.getenv('TZ')  这里会导致Cygwin和CMD中获取的时间相差一天
os.unsetenv('TZ')



class UserIntent( object ):
    def __init__( self ):
        self.defaultWorkDir = ''
        self.inputWorkDir   = ''
        self.operate        = ''
        self.platform       = ''
        self.data           = ''
        self.dataType       = ''
        self.userId         = ''
        self.productMax     = 2000   ## max download counter 
        self.pmax           = 5   ## max pthread
        self.playbackMax    = 100  ## playback download counter
        self.getKsFeed      = False
        self.getKsLive      = False
        self.getDyFeed      = False
        self.GetDyLive      = False
        self.dsxId          = ''
        self.defaultUidFile = ''
        self.defaultPlaybackUidFile = ''
        self.myKsUid        = '3xnzffmzps58emw'
        self.myDyUid        = ''
        self.myDaiduUid     = ''
        self.playbackUid    = ''
        self.pcursor        = ''

        self.srcDir            = ''
        self.dstDir            = ''
        self.fileManagerData   = [ ]
        self.defaultSrc        = ''
        self.defaultDst        = ''
        self.defaultUp         = ''
        self.up                = ''
        self.ksUidDefaultDir   = 'C:\\Users\\Administrator\\Desktop\\TEST\\'
        self.defaultProductDir = 'C:\\vc\\'
        self.zipPassword       = 'mojun' 



    ''' Convert cygwin path to windows path'''
    ''' If no classmthod, must UserIntent().ProcessCygPath(path)'''
    ''' path in method para must set to: path, no = '''
    @classmethod
    def ProcessCygPath( self, path='' ):
        path    = path.replace( '/cygdrive/','' ).replace('/', '\\' )
        lst     = list( path )
        lst[0]  = lst[0] + ':'
        path    = ''.join( lst )
        if os.path.isdir( path ) and ( path[-1]!='\\' ):
            path = path + '\\'
        return path

    ''' Check a string is ID or not'''
    @classmethod
    def IsLegalID( self, string='' ):
        legal = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', \
         'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',\
         '0','1','2','3','4','5','6','7','8','9']
        for c  in string:
            if not (c in legal):
                return False
        return True

    ''' Check a string is digit '''
    @classmethod
    def IsDigit( self, string='' ):
        digit = [ '0','1','2','3','4','5','6','7','8','9' ]
        for c in string:
            if not ( c in digit):
                return False
        return True


def ParseInputArgs( ):
    intent= UserIntent()
    parser = argparse.ArgumentParser(prog='suize')
    """=============================== downloader ============================================"""
    parser.add_argument( '-d', '--download', nargs='*',  type=str, 
                         help="""Download intent, sepcify ID or ID file.
                                Default read ID from local ID file.
                         """
                       )

    parser.add_argument( '-l', '--limit', nargs='?', type=int, const=2000, 
                         help="""Limit download counter of videos.
                                Default download all, but some ID have large count.
                         """
                       )
    parser.add_argument( '-db', '--download-back', nargs='?', const=intent.defaultPlaybackUidFile,  type=str,
                         help="""Download playback videos, If specify ID, donwload new playbakc video of ID,
                                 Otherwise read ID from local file."""
                       )
    parser.add_argument( '--get-myksfeed', action="store_true", default=False,
                         help="""Get my ks feed ID and author name, save to local file."""
                       )
    parser.add_argument( '--get-kslive', action="store_true", default=False, 
                         help="""Get my KS feed living room, output it's flv stream address.' """
                       )
    parser.add_argument( '--get-mydylive', action="store_true", default=False,
                         help="""Get my DY feed living room, output it's flv stream address.'"""
                       )
    parser.add_argument( '--get-mydyfeed', action="store_true", default=False,
                         help="""Get my DY feed info, output uid and nick name."""
                       ) 
    parser.add_argument( '--down-dsx', nargs='?', type=str,
                         help="""Download Duxiaoshi video from input ID. output a directort contain videos."""
                       )
    parser.add_argument( '--down-ixigua', nargs='?', type=str,
                         help="""Download Ixigua videos from url, If url is given, use it. else read url from local file."""
                       )
    parser.add_argument( '--down-haokan', nargs='?', type=str,
                         help="""Download Haokan video from UID. If url is given, user it. else read url from local file."""
                       )
    parser.add_argument( '-pmax', nargs='?', type=int, const=intent.pmax,
                         help="""Set max phread"""
                       )
    """================================= filemanager ======================================="""
    parser.add_argument( '--find-size', type=str, action='append', nargs=argparse.REMAINDER,
                         help="""Find FILE/DIR with specified size, srcDir, +/- size, fileType:DIR/FILE must input."""
                        )
    parser.add_argument( '--move-uid', nargs='?', const = intent.defaultSrc, type=str,
                         help="""Move src uid dir to author dir. If not specify, use default dir.  """
                       )
    parser.add_argument( '-to', nargs='?', const = intent.defaultDst, type=str,
                         help="""to dst dir, if no specify, user default dir."""
                       )
    parser.add_argument( '--rename-asauth', nargs=3, type=str, 
                         help="""srcDir  fileType: video/png/text....    recusion: True/False.
                                  Rename video file as parent dir (author) name. 
                                 If path is given,use it. Not will use default DIR.
                              """
                       )
    parser.add_argument( '--get-authname', nargs='?', const=intent.ksUidDefaultDir,
                         help="""Fetch author name from UID's Json file, Write UID-authorname to data file. '"""
                       )
    parser.add_argument( '-zip', nargs='?', const=intent.defaultProductDir,
                         help="""Zip compress file or dir to ZIP file."""
                       )
    parser.add_argument( '--del-same', type=str, action='append',  nargs=argparse.REMAINDER,
                         help="""Delete same file in src or dst. If dst is given. """
                    )
    parser.add_argument( '--gen-srt', type=str, nargs=1,
                         help="""Generate srt file of videos under given path."""
                       )
    parser.add_argument( '-p', nargs='?', type=str, const=intent.zipPassword,
                         help="""Set zip password. """
                       )
    """================================== mediaprocessor =================================="""
    parser.add_argument( '-concat', nargs=1, type=str,
                         help="""Concat all short video to one, If path sepcified, use it. else use default DIR."""
                       )
    parser.add_argument( '-encode', nargs=1, type=str,
                         help="""Encode concated video with FFMPEG h264, then delete it."""
                       )
    parser.add_argument( '--convert-flv', nargs=1, type=str,
                         help="""Convert Flvs to mp4. DIR/FLV file need. """
                       )
    parser.add_argument( '--clip-srt', nargs=1, type=str,
                         help="""Get awesome video clips from srt file."""
                       )
    parser.add_argument( '-cb', nargs=1, type=str,
                         help="""Merge play back ts file to mp4. """
                       )
    """================================== uploader =================================="""
    parser.add_argument( '-up', nargs=1, type=str,
                         help="""Upload loacal file to baiduyun. If path specified, use it. else: upload default dir."""
                       )
    """================================== facer =================================="""
    parser.add_argument( '--get-id', nargs=1, type=str,
                         help="""Get id from video logo."""
                      )
    parser.add_argument( '--search-id', nargs=1, type=str,
                        help="""Search id on webserver. return like: unique id of  user: 3xxxx. """
                       )
    parser.add_argument( '--face-id', nargs=1, type=str,
                        help="""Recogonize person in video, tell who they are, arrange them.  """
                       )
    parser.add_argument( '--gen-npy', nargs=1, type=str,
                        help="""Gen npy of all videos in dir. """
                       )
    """================================== logger =================================="""
    """No options for this model."""

    args = parser.parse_args() 

    ##print(args)
    """=============================== downloader ============================================"""
    ##print( '%-20s -ID File: %s' % ('[KS-Downloader]', path))
    ##print( '%-20s -With ID: %s' % ('[KS-Downloader]', id) )
    ##print( '%-20s -ID File: %s' % ('[KS-Downloader]', 'default'))
    ##print( '%-20s -Input: %s' % ('<E>Illegal', path) )
    lendownload=0
    if args.download:
        intent.operate  = 'download'
        intent.platform ='ks'
        lendownload     = len(args.download)
        if lendownload == 1:
            path = args.download[0]
            if 'cygdrive' in path:
                path = UserIntent.ProcessCygPath( path )
            if os.path.isfile( path ):
                intent.userId   = ''
                intent.data     = path 
                intent.dataType = 'FILE'
            else:
                if UserIntent.IsLegalID( path ):
                    intent.userId   = path 
                    intent.data     =  '' 
                    intent.dataType =  'STR'
                else:
                    intent = UserIntent( )
                    intent.operate='error'
        else:
            intent.data = []
            for uid in args.download:
                intent.data.append( uid )
            intent.dataType = 'LIST'
    elif args.download == None:
        pass
    else:
        intent.operate  = 'download'
        intent.platform = 'ks'
        intent.data     = 'default'
        intent.dataType = 'STR'

    if args.limit:
        intent.productMax  = args.limit
        intent.playbackMax = args.limit
    if (args.download_back) and( UserIntent.IsLegalID(args.download_back) ):
        intent.operate = 'download'
        intent.platform = 'ksplayback'
        intent.playbackUid = args.download_back 
        intent.dataType = 'STR'

    if args.get_myksfeed:
        ##intent.__init__( )
        intent.operate = 'get_myksfeed'
        intent.platform = 'ks'
        
    if args.get_kslive:
        intent.operate = 'get_mykslive'
        intent.platform = 'ks'
    if args.get_mydylive:
        intent.operate = 'get_mydylive'
        intent.pmax = 15
        intent.platform = 'dy'
    if args.get_mydyfeed:
        ##intent.__init__( )
        intent.operate = 'get_mydyfeed'
        intent.platform = 'dy'
    if args.down_dsx:
        intent.operate = 'down_dsx'
    if args.down_ixigua:
        print( 'down_ixigua - %s' % args.down_ixigua )
    if args.down_haokan:
        print( 'down_ixigua - %s' % args.down_haokan )
    if args.pmax:
        intent.pmax = args.pmax

    """================================= Filemanager ======================================="""
    if args.to  :
        intent.platform = 'filemanager'
        path = args.to
        if 'cygdrive' in path:
            path = UserIntent.ProcessCygPath( args.to )
        if os.path.isdir( path ):
            if path[-1] != '\\':
                path = path + '\\'
            intent.dstDir = path
        else:
            print('  <E> Invalid dst dir: %s' % path)
            exit()

    if args.move_uid: 
        intent.operate = 'move'
        intent.platform = 'filemanager'
        path = args.move_uid
        if 'cygdrive' in path:
            path = UserIntent.ProcessCygPath( args.move_uid )
        if os.path.isdir( path ):
            if path[-1] !='\\':
                path = path + '\\'
            intent.srcDir = path 

    if ( args.move_uid ) and ( args.to == None ):
        print( 'Move-uid,  -to option   needed!' )
        exit()
    
    if  args.find_size:
        afterString = args.find_size[0]
        if len( afterString ) != 3:
            print('  <Invalid Length of input args. validArgs: src, size, type:DIR/FILE >')
            exit()
        legalArgsSize = ['-', '+', 'M','m','G', 'g', 'K', 'k', 'DIR', 'FILE' ]
        intent.operate = 'find'
        intent.platform = 'filemanager' 
        path = ''
        if ( '/cygdrive/' in afterString[0] ):
            path = UserIntent.ProcessCygPath( afterString[0] )
        if os.path.isdir( path ):
            afterString[0] = path
            intent.fileManagerData = afterString
        else:
            print('  <Invalid input args. validArgs: src, size, type:DIR/FILE >')
            exit()
    ##print('Get %s  --%s ' % (intent.src, intent.dst))
    if args.rename_asauth:
        boolTrue  = ['true', True, 'True']
        boolFalse = [False, 'false', 'False']
        intent.operate = 'rename-asauth'
        intent.platform = 'filemanager'
        path = UserIntent.ProcessCygPath( args.rename_asauth[0] )
        if os.path.isdir( path ):
            args.rename_asauth[0] = path
            intent.fileManagerData = args.rename_asauth
        else:
            print('  <Invalid input args. validArgs: src, fileType/video/png/text/..., recusion/True/False >')
            exit()
        if (args.rename_asauth[2] in boolTrue):
            args.rename_asauth[2] = True
        elif (args.rename_asauth[2] in boolFalse):
            args.rename_asauth[2] = False 
        else:
            print('  <Invalid input args. validArgs: src, fileType, recusion/True/False >')
            exit()
        print( 'reaname_asauth - %s' % args.rename_asauth )
    if args.get_authname:
        intent.operate='parse'
        intent.platform='ks'
        path = UserIntent.ProcessCygPath( args.get_authname )
        intent.srcDir = path 
    if args.del_same:
        afterString = args.del_same[0]
        if len( afterString ) == 2:
            srcPath = afterString[0]
            dstPath = afterString[1]
            if '/cygdrive/' in srcPath:
                srcPath = UserIntent.ProcessCygPath( srcPath )
            if '/cygdrive/' in dstPath: 
                dstPath = UserIntent.ProcessCygPath( dstPath )
            if os.path.isdir( srcPath ):
                intent.srcDir = srcPath
            if os.path.isdir( dstPath ):
                intent.dstDir = dstPath
        elif len( afterString ) == 1:
            srcPath = afterString[0]
            if '/cygdrive/' in srcPath:
                srcPath = UserIntent.ProcessCygPath( srcPath )
            if os.path.isdir( srcPath ):
                intent.srcDir = srcPath
        else:
            print( '<E> del-same: input  error, src/dst is need.' )
            exit()
        intent.operate  = 'del_same'
        intent.platform = 'filemanager'
    if args.gen_srt:
        path = args.gen_srt[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.srcDir = path
            intent.operate = 'gen-srt'
            intent.platform = 'filemanager'
        else:
            print('  <* Gen-srt * Input option of video path Error. >')
            exit()
    if args.zip:
        path = args.zip
        intent.operate  = 'zip-files'
        intent.platform = 'filemanager'
        if '/cygdrive' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.srcDir   =  path
        if os.path.isfile( path ):
            intent.srcDir = path 
    if args.p:
        intent.zipPassword = args.p
    if args.p == None:
        intent.zipPassword = ''
        

    """================================== Mediaprocessor =================================="""
    if args.concat:
        print(args)
        path = args.concat[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.srcDir = path 
            intent.dstDir = ''
            intent.operate = 'concat-video'
            intent.platform = 'mediaprocessor'
        else:
            print('  <* Invail put. not DIR: %s .>' % path )
            exit()

    if args.encode:
        print( args )
        path = args.encode[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.srcDir = path 
            intent.dstDir = ''
            intent.operate = 'encode'
            intent.platform = 'mediaprocessor'
        else:
            print('  <* Invalid put. not DIR: %s .>' % path )
            exit()

    if args.convert_flv:
        print(args)
        path = args.convert_flv[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if ( os.path.isdir( path ) ) or ( os.path.isfile( path ) ):
            intent.srcDir = path 
            intent.dstDir = ''
            intent.operate = 'convert-flv'
            intent.platform = 'mediaprocessor'
        else:
            print('  <* Invail put. not DIR: %s .>' % path )
            exit()

    if args.clip_srt:
        print(args)
        srtPath   = args.clip_srt[0]
        if '/cygdrive' in  srtPath:
            srtPath = UserIntent.ProcessCygPath( srtPath )

        if os.path.isdir(srtPath):
            intent.operate = 'clip-srt'
            intent.platform = 'mediaprocessor'
            intent.srcDir   =  srtPath
        else:
            print( '  <** - Error: not valid path input .> ')
            exit( )
    if args.cb:
        print(args)
        tsPath  = args.cb[0]
        if '/cygdrive' in  tsPath:
            tsPath = UserIntent.ProcessCygPath( tsPath )

        if os.path.isdir( tsPath ):
            intent.operate = 'merge-ts'
            intent.platform = 'mediaprocessor'
            intent.srcDir   = tsPath 
        else:
            print( '  <** - Error: Invalid path input .> ')
            exit( )

    """================================== uploader =================================="""
    if args.up:
        print(args)
        path = args.up[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.operate = 'up-dir'
        if os.path.isfile( path ):
            intent.operate = 'up-file'
        intent.platform = 'uploader'
        intent.srcDir = path

    """================================== facer =================================="""
    if args.get_id:
        print(args)
        path = args.get_id[0]
        if '/cygdrive/' in path:
            path = UserIntent.ProcessCygPath( path )
        if os.path.isdir( path ):
            intent.operate = 'get-id-dir'
        if os.path.isfile( path ):
            intent.operate = 'get-id-file'
        intent.platform = 'facer'
        intent.srcDir = path

    if args.search_id:
        print(args)
        _str = args.search_id[0]
        if '/cygdrive/' in _str:
            _str = UserIntent.ProcessCygPath( _str )
        if os.path.isfile( _str ):
            intent.operate = 'search-id-file'
            intent.srcDir  = _str
            intent.platform = 'facer'
        elif os.path.isdir( _str ):
            pass
        else:
            if len( _str ) >= 8:
                intent.operate = 'search-id-string'
                intent.srcDir  = _str
                intent.platform = 'facer'
            else:
                print( '  <** - Input uid Error.> ')
    if args.face_id:
        print(args)
        _str = args.face_id[0]
        if '/cygdrive/' in _str:
            _str = UserIntent.ProcessCygPath( _str )
        if os.path.isfile( _str ):
            intent.operate = 'face-id-file'
            intent.srcDir   = _str
        if os.path.isdir( _str ):
            intent.operate = 'face-id-dir'
            intent.srcDir  = _str 
        intent.platform = 'facer'

    if args.gen_npy:
        print(args)
        _str = args.gen_npy[0]
        if '/cygdrive/' in _str:
            _str = UserIntent.ProcessCygPath( _str )
        if os.path.isdir( _str ):
            intent.operate = 'gen-npy'
            intent.srcDir  = _str
            intent.platform = 'facer'
        else:
            print( '  <** - Input: %s is not dir. .>' % _str )
            exit()


    return intent
if __name__ == "__main__":
    ParseInputArgs()
