#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: config 
# author: dreampuf

import os, sys
import logging
from cache import memcache
from model import _ConfigProperty

class CommentStatus(object):
    DISENABLE = 0
    ENABLE = 1
    USERONLY = 2
    NEEDCHECK = 4

class config(object):
    VERSION = 2.0
    CURPATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], "..")
    CHARSET = "utf-8"
    LANGUAGE = "zh-CN"
    
    APPID = os.environ["APPLICATION_ID"]
    BLOG_PATH = "/"
    BLOG_ADMIN_PATH = "/admin/"
    DOMAIN = _ConfigProperty("DOMAIN", os.environ['HTTP_HOST'])                       #站点域名
    TEMPLATE = _ConfigProperty("TEMPLATE", "iphonsta")
    POST_EDITOR = _ConfigProperty("POST_EDITOR", "")
    EDITOR_TYPE = ("html", "rest", "markdown", "bbcode")
    
    BASEURL = "http://%s" % (DOMAIN)
    ADMINURL = "%s%s" % (BASEURL, BLOG_ADMIN_PATH)
    TEMPLATEURL = "%s/template/%s" % (BASEURL, TEMPLATE)
    
    LOCAL_TIMEZONE = _ConfigProperty("LOCAL_TIMEZONE", 8)                               #时区
    TITLE = _ConfigProperty("TITLE", "bana")                                          #站点名称
    SUBTITLE = _ConfigProperty("SUBTITLE", "an other blog")                           #站点简介
    ENABLE_COMMENT = _ConfigProperty("ENABLE_COMMENT", True)                          #允许回复
    COMMENT_NEEDLOGINED = _ConfigProperty("COMMENT_NEEDLOGINED", False)               #回复需登录
    DESCRIPTION = _ConfigProperty("DESCRIPTION", "this descript in feed")             #FEED中的描述
    DATE_FORMAT = _ConfigProperty("DATE_FORMAT", "%Y-%m-%d")
    DATETIME_FORMAT = _ConfigProperty("DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S")
    DATEMINUTE_FORMAT = _ConfigProperty("DATEMINUTE_FORMAT", "%Y-%m-%d %H:%M")
    
    FEED_SRC = _ConfigProperty("FEED_SRC", "feed")
    FEEDURL = "%s/%s/" % ( BASEURL, FEED_SRC)
    FEED_NUMBER = _ConfigProperty("DIGIT_FEED_NUMBER_", 20)
    FEED_SUMMARY = _ConfigProperty("FEED_SUMMARY", False)
    FEED_COMMENT_COUNT = _ConfigProperty("FEED_COMMENT_COUNT", 5) 
    HUB_SRC = _ConfigProperty("HUB_SRC", ["http://pubsubhubbub.appspot.com/"])
    XML_RPC_ENDPOINT = _ConfigProperty("HUB_SRC", ['http://blogsearch.google.com/ping/RPC2', 'http://rpc.pingomatic.com/', 'http://ping.baidu.com/ping/RPC2'])
    
    INDEX_POST_COUNT = _ConfigProperty("INDEX_POST_COUNT", 10)
    INDEX_SUMMARY = _ConfigProperty("INDEX_SUMMARY", True)
    POST_PAGE_COUNT = _ConfigProperty("POST_PAGE_COUNT", 10)
    COMMENT_PAGE_COUNT = _ConfigProperty("COMMENT_PAGE_COUNT", 10)
    LAST_COMMENT_COUNT = _ConfigProperty("LAST_COMMENT_COUNT", 20)
    LAST_COMMENT_LENGTH = _ConfigProperty("LAST_COMMENT_LENGTH", 20)
    
    POST_CACHE_TIME = _ConfigProperty("POST_CACHE_TIME", 600)
    FEED_CACHE_TIME = _ConfigProperty("FEED_CACHE_TIME", 600)
    SITEMAP_CACHE_TIME = _ConfigProperty("SITEMAP_CACHE_TIME", 600)
    
    FOOTER_HTML = _ConfigProperty("FOOTER_HTML", "")
    HEAD_LINK = _ConfigProperty("HEAD_LINK", ["/js/common.js"])
    POST_URL = _ConfigProperty("POST_URL", "%year%/%month%/%url%.html")
    
    COMMENT_STATUS = _ConfigProperty("COMMENT_STATUS", CommentStatus.ENABLE)
    
    RECAPTCHA_PUBLIC_KEY = _ConfigProperty("RECAPTCHA_PUBLIC_KEY","6Le-a78SAAAAAPBtWkwwMmwsk21LWhA-WySPzY5o")
    RECAPTCHA_PRIVATE_KEY = _ConfigProperty("RECAPTCHA_PRIVATE_KEY", "6Le-a78SAAAAAPpK1K0hm5FuyOBU7KPJmJxxMjas")
    GOOGLE_ANALYTICS_ID = _ConfigProperty("GOOGLE_ANALYTICS_ID", "")





config = config()
