#coding:utf-8
import base64

class NoAds:
    """
    # 功能:从url得到ID
    """
    @staticmethod
    def getUrlId(url):

        if not 'http' in url:
           id = NoAds.flvDeId(url)
        elif 'v=' in url:
            id = url.strip().split('v=')[1]
            id = id.replace('.html', '')
            id = NoAds.flvDeId(id)
        elif 'v_' in url:
            id = url.strip().split('v_')[1]
            id = id.replace('.html', '')
            id = NoAds.flvDeId(id)
        elif 'vid-' in url:
            id = url.strip().split('vid-')[1]
            id = id.replace('.html', '')
            id = NoAds.flvDeId(id)
        elif '.html' in url:
            id = url.strip().split('/id')[1]
            id = id.replace('.html', '')
        else:
            id = url.strip().split('id=')[1]
            id = id.split('&')
            id = id[0]

        return id

    """
    功能: 解密flvid
    参数: string BASE64
    返回: id    FLVID
    """
    @staticmethod
    def flvDeId(id):
        if str(id).isdigit():
            return id
        else:
            return int(base64.b64decode(id))
