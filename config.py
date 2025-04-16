#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Configuration for Bana
# Author: dreampuf (original), updated by Codegen

import os
import sys
import logging
from models.base import ConfigProperty

class CommentStatus:
    """Comment status constants"""
    DISENABLE = 0
    ENABLE = 1
    USERONLY = 2
    NEEDCHECK = 4

class Config:
    """Configuration class for Bana"""
    VERSION = 2.0
    CURPATH = os.path.dirname(os.path.abspath(__file__))
    CHARSET = "utf-8"
    LANGUAGE = "zh-CN"
    
    # App settings
    APPID = os.environ.get("GOOGLE_CLOUD_PROJECT", "hxbana")
    OWNER = ConfigProperty("OWNER", "soddyque@gmail.com")
    BLOG_PATH = "/"
    BLOG_ADMIN_PATH = "/admin/"
    DOMAIN = ConfigProperty("DOMAIN", os.environ.get('HTTP_HOST', 'huangxin.im'))
    TEMPLATE = ConfigProperty("TEMPLATE", "iphonsta")
    POST_EDITOR = ConfigProperty("POST_EDITOR", "")
    EDITOR_TYPE = ("html", "rest", "markdown", "bbcode")
    
    # URLs
    BASEURL = f"https://{DOMAIN}"
    ADMINURL = f"{BASEURL}{BLOG_ADMIN_PATH}"
    TEMPLATEURL = f"{BASEURL}/template/{TEMPLATE}"
    
    # Time and display settings
    LOCAL_TIMEZONE = ConfigProperty("LOCAL_TIMEZONE", 8)
    TITLE = ConfigProperty("TITLE", "bana")
    SUBTITLE = ConfigProperty("SUBTITLE", "an other blog")
    ENABLE_COMMENT = ConfigProperty("ENABLE_COMMENT", True)
    COMMENT_NEEDLOGINED = ConfigProperty("COMMENT_NEEDLOGINED", False)
    DESCRIPTION = ConfigProperty("DESCRIPTION", "this descript in feed")
    DATE_FORMAT = ConfigProperty("DATE_FORMAT", "%Y-%m-%d")
    DATETIME_FORMAT = ConfigProperty("DATETIME_FORMAT", "%Y-%m-%d %H:%M:%S")
    DATEMINUTE_FORMAT = ConfigProperty("DATEMINUTE_FORMAT", "%Y-%m-%d %H:%M")
    
    # Feed settings
    FEED_SRC = ConfigProperty("FEED_SRC", "feed/")
    FEED_URL = f"{BASEURL}/{FEED_SRC}"
    FEED_NUMBER = ConfigProperty("DIGIT_FEED_NUMBER_", 20)
    FEED_SUMMARY = ConfigProperty("FEED_SUMMARY", False)
    FEED_COMMENT_COUNT = ConfigProperty("FEED_COMMENT_COUNT", 5)
    HUB_SRC = ConfigProperty("HUB_SRC", ["http://pubsubhubbub.appspot.com/"])
    XML_RPC_ENDPOINT = ConfigProperty("HUB_SRC", [
        'http://blogsearch.google.com/ping/RPC2',
        'http://rpc.pingomatic.com/',
        'http://ping.baidu.com/ping/RPC2'
    ])
    
    # Content settings
    INDEX_POST_COUNT = ConfigProperty("INDEX_POST_COUNT", 10)
    INDEX_SUMMARY = ConfigProperty("INDEX_SUMMARY", True)
    POST_PAGE_COUNT = ConfigProperty("POST_PAGE_COUNT", 10)
    COMMENT_PAGE_COUNT = ConfigProperty("COMMENT_PAGE_COUNT", 10)
    LAST_COMMENT_COUNT = ConfigProperty("LAST_COMMENT_COUNT", 20)
    LAST_COMMENT_LENGTH = ConfigProperty("LAST_COMMENT_LENGTH", 20)
    
    # Cache settings
    POST_CACHE_TIME = ConfigProperty("POST_CACHE_TIME", 600)
    FEED_CACHE_TIME = ConfigProperty("FEED_CACHE_TIME", 600)
    SITEMAP_CACHE_TIME = ConfigProperty("SITEMAP_CACHE_TIME", 600)
    
    # HTML settings
    FOOTER_HTML = ConfigProperty("FOOTER_HTML", "")
    HEAD_LINK = ConfigProperty("HEAD_LINK", ["/js/common.js"])
    POST_URL = ConfigProperty("POST_URL", "%year%/%month%/%url%.html")
    
    # Comment settings
    COMMENT_STATUS = ConfigProperty("COMMENT_STATUS", CommentStatus.ENABLE)
    
    # External services
    RECAPTCHA_PUBLIC_KEY = ConfigProperty("RECAPTCHA_PUBLIC_KEY", "6Le-a78SAAAAAPBtWkwwMmwsk21LWhA-WySPzY5o")
    RECAPTCHA_PRIVATE_KEY = ConfigProperty("RECAPTCHA_PRIVATE_KEY", "6Le-a78SAAAAAPpK1K0hm5FuyOBU7KPJmJxxMjas")
    GOOGLE_ANALYTICS_ID = ConfigProperty("GOOGLE_ANALYTICS_ID", "")

# Create a singleton instance
config = Config()
