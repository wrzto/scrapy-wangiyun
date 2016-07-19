#-*-coding:utf-8-*-


from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors  import LinkExtractor
from wangyiyun.items import WangyiyunItem
from scrapy.http import FormRequest

import requests
import json
import os
import base64
from Crypto.Cipher import AES


class MusicSpider(CrawlSpider):
    name = 'wangyiyun'
    allowed_domains=["music.163.com"]
    start_urls=["http://music.163.com/discover/artist"]
    rules = [Rule(LinkExtractor(allow=(r'/discover/artist/cat\?id=\d+'))),
             Rule(LinkExtractor(allow=(r'/artist\?id=\d+'))),
             Rule(LinkExtractor(allow=(r'/discover/artist/cat\?id=\d+&initial=\d+'))),
             Rule(LinkExtractor(allow=(r'/song\?id=\d+')),callback="parse_song")]



    def parse_song(self,response):
        sel=Selector(response)
        item=WangyiyunItem()
        comments_api='http://music.163.com/weapi/v1/resource/comments/R_SO_4_'+response.url[29:]+'/?csrf_token='
        item['music_name']=sel.xpath('//em[@class="f-ff2"]/text()').extract()
        item['artist']=sel.xpath('//p[@class="des s-fc4"]/span/a/text()').extract()
        item['special']=sel.xpath('//p[@class="des s-fc4"]/a/text()').extract()
        item['comments']=self.get_comments(comments_api)
        item['song_url']=response.url

        return item

    #以下为评论区API，来自知乎
    #知乎链接：http://www.zhihu.com/question/36081767/answer/65820705
    def aesEncrypt(self,text, secKey):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(secKey, 2, '0102030405060708')
        ciphertext = encryptor.encrypt(text)
        ciphertext = base64.b64encode(ciphertext)
        return ciphertext


    def rsaEncrypt(self,text, pubKey, modulus):
        text = text[::-1]
        rs = int(text.encode('hex'), 16) ** int(pubKey, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)


    def createSecretKey(self,size):
        return (''.join(map(lambda xx: (hex(ord(xx))[2:]), os.urandom(size))))[0:16]

    def get_comments(self,url):
        headers = {
            'Cookie': 'appver=1.5.0.75771;',
            'Referer': 'http://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.8 Safari/537.36'
        }
        text = {
            'username': '邮箱',
            'password': '密码',
            'rememberLogin': 'true'
        }
        modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        nonce = '0CoJUm6Qyw8W8jud'
        pubKey = '010001'
        text = json.dumps(text)
        secKey = self.createSecretKey(16)
        encText = self.aesEncrypt(self.aesEncrypt(text, nonce), secKey)
        encSecKey = self.rsaEncrypt(secKey, pubKey, modulus)
        data = {
            'params': encText,
            'encSecKey': encSecKey
        }
        try:
            req = requests.post(url, headers=headers, data=data,timeout=1)
            print u'API获取成功'
        except Exception,e:
            print u'API获取失败'
            print e
            return -1
        return req.json()['total']






