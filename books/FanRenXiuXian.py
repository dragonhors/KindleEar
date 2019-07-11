#!/usr/bin/env python
# -*- coding:utf-8 -*-

from datetime import datetime # 导入时间处理模块datetime
from base import BaseFeedBook # 继承基类BaseFeedBook
from lib.urlopener import URLOpener # 导入请求URL获取页面内容的模块
from bs4 import BeautifulSoup # 导入BeautifulSoup处理模块

# 返回此脚本定义的类名
def getBook():
    return Fanren_Test

# 继承基类BaseFeedBook
class Fanren_Test(BaseFeedBook):
    # 设定生成电子书的元数据
    title = u'003.凡人修仙传仙界篇'                   # 设定订阅项目显示标题
    __author__ = u'妄语'                              # 设定作者，目前未用到
    description = u'妄语'                             # 设定简介，订阅项目上显示
    language = 'zh-cn'                                # 设定语言

    #coverfile = 'cv_Fanren.jpg' # 设定封面图片
    #mastheadfile = 'mh_novelbook.gif' # 设定标头图片
      
    # 指定要提取的包含文章列表的主题页面链接
    # 每个主题是包含主题名和主题页面链接的元组
    feeds = [
        (u'凡人修仙', 'https://www.xbiquge6.com/1_1203/'),
    ]

    page_encoding = 'utf-8'                             # 设定待抓取页面的页面编码
    fulltext_by_readability = False                     # 设定手动解析网页

    # 设定内容页需要保留的标签
    keep_only_tags = [
        dict(name='div',id='content'),
    ]
    #是否按星期投递，留空则每天投递，否则是一个星期字符串列表
    #一旦设置此属性，则网页上设置的“星期推送”对此书无效
    #'Monday','Tuesday',...,'Sunday'，大小写敏感
    #比如设置为['Friday'] 或 ['Monday','Tuesday','Wednesday','Thursday','Friday', 'Sunday']
    deliver_days = ['Wednesday','Saturday']

    #自定义书籍推送时间，一旦设置了此时间，则网页上设置的时间对此书无效
    #用此属性还可以实现一天推送多次
    #格式为整形列表，比如每天8点/18点推送，则设置为[8,18]
    #时区则自动使用订阅者的时区
    deliver_times = []

    max_articles_per_feed = 10 # 设定每个主题下要最多可抓取的文章数量
    #oldest_article = 1 # 设定文章的时间范围。小于等于365则单位为天，否则单位为秒，0为不限制。

    # 提取每个主题页面下所有文章URL
    def ParseFeedUrls(self):
        urls = [] # 定义一个空的列表用来存放文章元组
        # 循环处理feeds中两个主题页面
        for feed in self.feeds:
            # 分别获取元组中主题的名称和链接
            topic, url = feed[0], feed[1]
            # 把抽取每个主题页面文章链接的任务交给自定义函数ParsePageLinks()
            self.ParsePageLinks(topic, url, urls, count=0,count2=0,ccc=0)
        # 返回提取到的所有文章列表
        return urls

    # 该自定义函数负责单个主题下所有文章链接的抽取，如有翻页则继续处理下一页
    def ParsePageLinks(self, topic, url, urls, count,count2,ccc):
        # 请求主题页面或章节列表页面的链接和内容
        result = self.GetResponseContent(url)
        # 如果请求成功，并且页面内容不为空
        if result.status_code == 200 and result.content:
            # 将主题或列表页面内容转换成BeatifulSoup对象
            soup = BeautifulSoup(result.content, 'lxml')
            # 找出当前页面文章列表中所有文章条目，里面的标签参数需要手工修改确认
            items = soup.find_all(name='dd')
            #获取总章节数，以便抓取最新章节，追更---应该有个函数能使用，可惜我不知道啊
            for ttt in items:
                ccc += 1

            # 循环处理每个文章条目
            for item in items:
                title = item.a.string # 获取文章标题
                link = item.a.get('href') # 获取文章链接
                link = BaseFeedBook.urljoin(url, link) # 合成文章链接
                count += 1 # 统计当前已处理的文章条目
                
                # 如果处理的文章条目超过了设定数量则中止抽取，改动下面的条件限制，选择抓取方式，都屏蔽掉，则抓全部
                count2 = count + self.max_articles_per_feed 
                if count2 < ccc:                                                             #一、从最后抓n章
                    continue
                    
                #if count > self.max_articles_per_feed:                                      #二、从前面抓n章
                #    break
                
                # 将符合设定文章数量的文章信息作为元组加入列表
                urls.append((topic, title, link, None))

            # 如果主题页面有下一页，且已处理的文章条目未超过设定数量，则继续抓取下一页，递进调用自己
            #next = soup.find(name='a', string='Next')
            #if next and count < self.max_articles_per_feed:
                #url = BaseFeedBook.urljoin(url, next.get('href'))
                #self.ParsePageLinks(topic, url, urls, count)
        # 如果请求失败则打印在日志输出中
        else:
            self.log.warn('Fetch article failed(%s):%s' % \
                (URLOpener.CodeMap(result.status_code), url))

    # 此函数负责判断文章是否超出指定时间范围，是返回 True，否则返回False

    # 清理文章URL附带字符
    def processtitle(self, title):
        return title.replace(u'-凡人修仙之仙界篇 - 新笔趣阁', '')

    # 在文章内容被正式处理前做一些预处理
    def preprocess(self, content):
        # 将页面内容转换成BeatifulSoup对象
        soup = BeautifulSoup(content, 'lxml')
        # 调用处理内容分页的自定义函数 SplitJointPagination()
        content = self.SplitJointPagination(soup)
        # 返回预处理完成的内容
        return unicode(content)

    # 此函数负责处理文章内容页面的翻页
    def SplitJointPagination(self, soup):
        # 如果文章内容有下一页则继续抓取下一页
        next = soup.find(name='a', string='Next')
        if next:
            # 含文章正文的标签
            tag = dict(name='div', id='Content')
            # 获取下一页的内容
            result = self.GetResponseContent(next.get('href'))
            post = BeautifulSoup(result.content, 'lxml')
            # 将之前的内容合并到当前页面
            soup = BeautifulSoup(unicode(soup.find(**tag)), 'html.parser')
            soup.contents[0].unwrap()
            post.find(**tag).append(soup)
            # 继续处理下一页
            return self.SplitJointPagination(post)
        # 如果有翻页，返回拼接的内容，否则直接返回传入的​内容
        return soup

    # 此自定义函数负责请求传给它的链接并返回响应内容
    def GetResponseContent(self, url):
        opener = URLOpener(self.host, timeout=self.timeout, headers=self.extra_header)
        return opener.open(url)