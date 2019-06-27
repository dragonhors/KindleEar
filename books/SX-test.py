#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime # 导入时间处理模块datetime
from base import BaseFeedBook # 继承基类BaseFeedBook
from lib.urlopener import URLOpener # 导入请求URL获取页面内容的模块
from bs4 import BeautifulSoup # 导入BeautifulSoup处理模块

# 返回此脚本定义的类名
def getBook():
    return sxtest

# 继承基类BaseFeedBook
class sxtest(BaseFeedBook):
    # 设定生成电子书的元数据
    title = u'圣墟test' # 设定标题
    __author__ = u'辰东' # 设定作者
    description = u'在破败中崛起，在寂灭中复苏。' # 设定简介
    #language = 'en' # 设定语言

    #coverfile = 'cv_chinadaily.jpg' # 设定封面图片
    #mastheadfile = 'mh_chinadaily.gif' # 设定标头图片

    # 指定要提取的包含文章列表的主题页面链接
    # 每个主题是包含主题名和主题页面链接的元组
    feeds = [
        (u'小说圣墟', 'https://www.xbiquge6.com/74_74821/')
          ]

    page_encoding = 'utf-8' # 设定待抓取页面的页面编码
    fulltext_by_readability = False # 设定手动解析网页

    # 设定内容页需要保留的标签
    keep_only_tags = [
        dict(name='div', class_='bookname'),
        dict(name='div', id='Content'),
    ]

    max_articles_per_feed = 40 # 设定每个主题下要最多可抓取的文章数量
    oldest_article = 2 # 设定文章的时间范围。小于等于365则单位为天，否则单位为秒，0为不限制。

    # 提取每个主题页面下所有文章URL
    def ParseFeedUrls(self):
        urls = [] # 定义一个空的列表用来存放文章元组
        # 循环处理feeds中两个主题页面
        for feed in self.feeds:
            # 分别获取元组中主题的名称和链接
            topic, url = feed[0], feed[1]
            # 把抽取每个主题页面文章链接的任务交给自定义函数ParsePageContent()
            self.ParsePageContent(topic, url, urls, count=0)
        print urls
        exit(0)
        # 返回提取到的所有文章列表
        return urls

    # 该自定义函数负责单个主题下所有文章链接的抽取，如有翻页则继续处理下一页
    def ParsePageContent(self, topic, url, urls, count):
        # 请求主题页面链接并获取其内容
        result = self.GetResponseContent(url)
        # 如果请求成功，并且页面内容不为空
        if result.status_code == 200 and result.content:
            # 将页面内容转换成BeatifulSoup对象
            soup = BeautifulSoup(result.content, 'lxml')
            # 找出当前页面文章列表中所有文章条目
            items = soup.find_all(name='div', class_='box_con')

            # 循环处理每个文章条目
            for item in items:
                title = item.a.string # 获取文章标题
                link = item.a.get('href') # 获取文章链接
                link = BaseFeedBook.urljoin(url, link) # 合成文章链接
                count += 1 # 统计当前已处理的文章条目
                # 如果处理的文章条目超过了设定数量则中止抽取
                if count > self.max_articles_per_feed:
                    break
                # 将符合设定文章数量和时间范围的文章信息作为元组加入列表
                urls.append((topic, title, link, None))

            如果主题页面有下一页，且已处理的文章条目未超过设定数量，则继续抓取下一页
            next = soup.find(name='a', string='Next')
            if next and count < self.max_articles_per_feed:
                url = BaseFeedBook.urljoin(url, next.get('href'))
                self.ParsePageContent(topic, url, urls, count)
        # 如果请求失败则打印在日志输出中
        else:
            self.log.warn('Fetch article failed(%s):%s' % \
                (URLOpener.CodeMap(result.status_code), url))

    # 此自定义函数负责请求传给它的链接并返回响应内容
    def GetResponseContent(self, url):
        opener = URLOpener(self.host, timeout=self.timeout, headers=self.extra_header)
        return opener.open(url)