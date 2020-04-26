# EasynetComments
* 基于aiohttp的异步爬虫
* 类GetAlbumSongId获取网易云音乐对应的歌手的所有歌曲的id
* 类EasynetComments获取评论数据
    * 方法aes、rsa用来模拟加密，random_str用来产生随机数，产生的随机数用来作为aes第二次加密的秘钥以及rsa加密的明文
    * 方法get_hot_comments获取第一页数据，包含最热评论，方法get_comment获取其他的评论，方法get_comments_json用来解析json存储数据
    
 