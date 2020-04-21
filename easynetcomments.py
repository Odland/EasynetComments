"""获取网易云某个歌手的所有歌曲的评论数据"""

import random
import math
from Crypto.Cipher import AES
import base64
import codecs
import requests
import json
import pymongo
import random
import time
import sys

import numpy as np
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

myclient = pymongo.MongoClient("mongodb://{}:{}@{}:{}/{}".format("数据库的拥有者","密码","ip地址","端口号","数据库名"))
db = myclient.easynet


class  GetAlbumSongId(object):
    """获取歌曲的专辑以及专辑对应的id"""
    def get_album(self,artist_id = '5770',number = '27'):
        """
        获取歌手所有专辑的id
        并将含有id的list返回
        默认的是许巍的专辑数量
        """
        url = 'http://music.163.com/api/artist/albums/{}?id={}&offset=0&total=true&limit={}'.format(artist_id,artist_id,number)
        r = requests.get(url)
        js = json.loads(r.text)
        # 以专辑id:专辑歌曲数目字典的形式传递数据
        return {album_id["id"]:album_id["size"] for album_id in js["hotAlbums"]}
    
    def get_song(self,album_id='74992234',number='10'):
        """
        获取专辑里的歌曲id
        默认是许巍第一个专辑id,默认获取10首歌曲
        """       
        url = 'http://music.163.com/api/album/{}?ext=true&id={}&offset=0&total=true&limit={}'.format(album_id,album_id,number)
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "_iuqxldmzr_=32; _ntes_nuid=49bebcf2138e780caeb61619a000d594; mail_psc_fingerprint=80064039fd358f6e00d573df1ae8cc70; nts_mail_user=wying256257@163.com:-1:1; _ga=GA1.2.286849611.1540559883; __utma=94650624.1150172515.1538034295.1546170276.1546571490.313; ntes_kaola_ad=1; vinfo_n_f_l_n3=66c779836f1dd7b1.1.0.1568209787930.0.1568209881627; WM_TID=kMSCQbaGqGlAVFQVEENt8jaQh0BG9abd; _ntes_nnid=49bebcf2138e780caeb61619a000d594,1569658416293; WM_NI=CbQusVUuG0YBBFuM2y%2FSuX8Ubgc0zHcW%2BIGWETfPF0y0KtVOXZNv5DtVn%2F6X2PFsheH5ooSodxAoIdTavEStV2FdY4gq24Gp35FAt35ELi6cv5zSAuKdnws0yUzQ8Qa2Zmc%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee96c97abcf1bbb2cb5993ef8bb6d45e978a9eaef15fbabe8eb0b17dba9ebb8eb72af0fea7c3b92a81be9f96f25e97ab89d1dc4a829abbaeb173ed8dbbb9bb5fa2b9add1f944a189e5aac65d878caab1c53cbbf08595d5459c868297b850b88aa2d0b554f2908a94eb6f8ceba190d265a8a88f90cc7098bfbaa6d28096ee8a85dc40a5affed5c67cf1eb8aa2f739f79b848ab569b6ebb6b4c47f89bca298f23cbb8bb6b2bb5ba3ee968ee237e2a3; JSESSIONID-WYYY=mxrdeZ32l6P6bt9l4yVJ7SW%5CPad6UFxGrQ4SvPkxAAw5FPRyrYU5dFGE8%5CHONp2DYZcmMCWhwvM7q0bhdkCF7bmIN5C8s2ehQBNBQHl5EDjzXty2n9W7OySRh3Zb7oNurZ9xOhp9BY5JIpDOCyrXzJQ%2F4g0f2U9UYNn8qJoc4yrc6FEr%3A1586341510332",
            "Host": "music.163.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36",
        }
        r = requests.get(url,headers=headers)
        js = json.loads(r.text)
        # js["album"]["songs"][1]["id"]
        number = int(number)
        # 以列表的形式存储所有歌曲id
        song_ids = [js["album"]["songs"][i]["id"] for i in range(number)]
        return song_ids

        
class EasynetComments(object):
    """模拟加密参数,获取网易云音乐"""

    def __init__(self,key = '0CoJUm6Qyw8W8jud',
                    n = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
                    e = '010001'):
        # aes加密所需的秘钥
        self.key = key
        # rsa加密所需的模数
        self.n = n
        # rsa加密所需的随机质数16进制
        self.e = e 
        # 爬取所需的headers
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            "Content-Lenth":"474",
            #  'Cookie': 'WM_TID=36fj4OhQ7NdU9DhsEbdKFbVmy9tNk1KM; _iuqxldmzr_=32; _ntes_nnid=26fc3120577a92f179a3743269d8d0d9,1536048184013; _ntes_nuid=26fc3120577a92f179a3743269d8d0d9; __utmc=94650624; __utmz=94650624.1536199016.26.8.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); WM_NI=2Uy%2FbtqzhAuF6WR544z5u96yPa%2BfNHlrtTBCGhkg7oAHeZje7SJiXAoA5YNCbyP6gcJ5NYTs5IAJHQBjiFt561sfsS5Xg%2BvZx1OW9mPzJ49pU7Voono9gXq9H0RpP5HTclE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eed5cb8085b2ab83ee7b87ac8c87cb60f78da2dac5439b9ca4b1d621f3e900b4b82af0fea7c3b92af28bb7d0e180b3a6a8a2f84ef6899ed6b740baebbbdab57394bfe587cd44b0aebcb5c14985b8a588b6658398abbbe96ff58d868adb4bad9ffbbacd49a2a7a0d7e6698aeb82bad779f7978fabcb5b82b6a7a7f73ff6efbd87f259f788a9ccf552bcef81b8bc6794a686d5bc7c97e99a90ee66ade7a9b9f4338cf09e91d33f8c8cad8dc837e2a3; JSESSIONID-WYYY=G%5CSvabx1X1F0JTg8HK5Z%2BIATVQdgwh77oo%2BDOXuG2CpwvoKPnNTKOGH91AkCHVdm0t6XKQEEnAFP%2BQ35cF49Y%2BAviwQKVN04%2B6ZbeKc2tNOeeC5vfTZ4Cme%2BwZVk7zGkwHJbfjgp1J9Y30o1fMKHOE5rxyhwQw%2B%5CDH6Md%5CpJZAAh2xkZ%3A1536204296617; __utma=94650624.1052021654.1536048185.1536199016.1536203113.27; __utmb=94650624.12.10.1536203113',
            'Host': 'music.163.com',
            "origin":"https://music.163.com",
            'Referer': 'http://music.163.com/',
            'Upgrade-Insecure-Requests': '1',
            "Sec-Fetch-Dest":"empty",
            "Sec-Fetch-Mode":"cors",
            "Sec-Fetch-Site":"same-origin",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/66.0.3359.181 Safari/537.36'}
        
    def aes(self,msg,key):
        # key = '0CoJUm6Qyw8W8jud'
        # msg = '{"csrf_token":""}'
        iv = '0102030405060708'
        padding = 16 - len(msg) % 16
        msg = msg + padding * chr(padding)
        # print(msg)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        # 加密后得到的是bytes类型的数据
        encryptedbytes = cipher.encrypt(msg)
        # print(encryptedbytes)
        # 使用Base64进行编码,返回byte字符串
        encodestrs = base64.b64encode(encryptedbytes)
        # print(encodestrs)
        # 对byte字符串按utf-8进行解码
        enctext = encodestrs.decode('utf-8')
        # print(enctext)
        return enctext
        
    def rsa(self,n,e,m):
        m = m[::-1]
        msg = bytes(m,"utf-8")
        # seckey = int(codecs.encode(msg, encoding='hex'), 16)**int(e, 16) % int(n, 16)
        a = np.array([int(codecs.encode(msg, encoding='hex'), 16)**int(e, 16)])
        b = np.array([int(n, 16)])
        seckey = np.mod(a,b)[0]
        return format(seckey, 'x').zfill(256)

    def random_str(self,length=16):
        """获得一个16位的随机字符串"""
        # 随机生成16位字符作为rsa明文并在第二次aes加密时作为密钥
        string = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        string_length = len(string)
        string_new = ""
        for i in range(length):
            e = random.random() * string_length
            num = math.floor(e)
            string_new += string[num]
        # 也可用这种方式,并且发现随机范围在改变的情况下不影响程序数据的获取
        # for i in range(length):
        #     random_strs += string[random.randint(0,61)]
        return string_new
    
    def get_hot_comments(self,songid,msg = '{"limit":"20","csrf_token":""}'):
        # 获取第一页数据 包括热评和最新的评论
        istr = self.random_str()
        enctext = self.aes(msg,self.key)
        encText = self.aes(enctext, istr)
        # RSA加密之后得到encSecKey的值
        encSecKey = self.rsa(self.n, self.e, istr)
        data = {'params': encText, 'encSecKey': encSecKey}
        url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token=".format(songid)
        # try:
        f = 0
        while f<3:  
            try:
                r = requests.post(url, headers=self.headers, data=data,verify=False)
                r.encoding = "utf-8"
                if r.status_code == 200:
                    # 返回json格式的数据
                    ss = json.loads(r.text)
                    # print(type(ss))
                    # print(ss["total"])
                    # print(ss)
                    # print("歌曲id是",songid )
                    # 将热门的评论存储到mongodb中集合hotcomments中
                    total = int(ss["total"])
                    if total == 0:
                        return 0
                    for i in ss["hotComments"]:
                        # 存储评论者的信息
                        # 加入歌曲id
                        i.update({"songid":songid})
                        db.hot_tmp_comments.insert_one(i)
                    # with open("sb.json","w") as f:
                    #     f.write(ss)
                    # 存储普通的最新评论
                    for i in ss["comments"]:
                        i.update({"songid":songid})
                        db.test_comments.insert_one(i)
                    return ss["total"]
            except Exception as e:
                f += 1
                print("获取精彩数据失败",e)
        return 0
        # except Exception as e:
        #     print("爬取失败!",e)
    
    def get_comment(self,songid,num):
        """获取其余的评论"""
        # msg = '{"limit":"20","csrf_token":""}'
        istr = self.random_str()
        msg = '{"offset":"'+str(num)+'","total":"false","limit":"100","csrf_token":""}'
        url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_{}?csrf_token=".format(songid)
        enctext = self.aes(msg,self.key)
        encText = self.aes(enctext, istr)
        # RSA加密之后得到encSecKey的值
        encSecKey = self.rsa(self.n, self.e, istr)
        data = {'params': encText, 'encSecKey': encSecKey}
        self.get_comments_json(url,data,songid)

    def get_comments_json(self,url, data,songid):
        # flag = True
        f = 0
        while f<3:  
            try:
                time.sleep(random.random())
                r = requests.post(url, headers=self.headers, data=data,verify=False)
                r.encoding = "utf-8"
                # if r.status_code == 200:
                # 返回json格式的数据
                # print(r.json()['comments'])
                ss = json.loads(r.text)
                # 存入数据库
                # print(ss)
                print(ss["comments"])
                for i in ss["comments"]:
                    i.update({"songid":songid})
                    db.test_comments.insert_one(i)
                    print("评论",i["content"])
                    print("评论者id",i["user"]["userId"])
                #     print("入库了")
                # print("存入数据库")
                return
                # 存入数据库
                # with open("sb.json","w") as f:
                #     f.write(ss)
            except Exception as e:
                print("爬取失败!",e)
                # flag = False
                f += 1
            return
    

def main():
    getalbumsongid = GetAlbumSongId()
    album = getalbumsongid.get_album()
    for id_dict in album.keys():
        # 获取了一个专辑所有的歌曲id
        for songid in getalbumsongid.get_song(id_dict,album[id_dict]):
            easynetcomments = EasynetComments()
            # 获取精彩评论和最新评论并将评论数返回
            # songid = "167837"
            number = easynetcomments.get_hot_comments(songid)
            number = int(number)
            print("歌曲总数",number)
            # 评论数小于20,直接抓取下一首歌曲评论
            if number <= 20:
                print("小于20")
                continue
            # limit=100,偏移量从20开始获取剩下的评论
            page = int((number-20)/100)+1
            number_int = int(number)
            alist = []
            for i in range(1,page):
                alist.append(i)
            i = 0
            while len(alist)>0:
                pag = random.choice(alist)
                alist.remove(pag)
                pag = pag*100+20
                print("第",i,"页")
                easynetcomments.get_comment(songid,pag)
                i+=1
        

if __name__ == "__main__":
    main()
    
    





    