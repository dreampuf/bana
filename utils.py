#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Utility functions for Bana
# Author: dreampuf (original), updated by Codegen

import os
import random
import string
import datetime
import hashlib
import logging
from config import config

def format_content(content, format="html"):
    """Format content based on the specified format"""
    if format == "html":
        return content
    elif format == "rest":
        try:
            from docutils.core import publish_parts
            doc = publish_parts(
                content,
                writer_name='html',
                settings_overrides={
                    "file_insertion_enabled": 0,
                    "raw_enabled": 0,
                    "_disable_config": 1,
                }
            )
            return doc["body"]
        except ImportError as ex:
            logging.error(f"Error importing docutils: {ex}")
            return content
    elif format == "markdown":
        try:
            import markdown
            return markdown.markdown(content, output_format="html4")
        except ImportError as ex:
            logging.error(f"Error importing markdown: {ex}")
            return content
    elif format == "bbcode":
        try:
            import postmarkup
            return postmarkup.render_bbcode(content, encoding=config.CHARSET, paragraphs=True)
        except ImportError as ex:
            logging.error(f"Error importing postmarkup: {ex}")
            return content
    return content

def randstr(start=5, end=10, case=string.ascii_lowercase):
    """Generate a random string"""
    return "".join([random.choice(case) for i in range(random.randint(start, end))])

def gender_url(url, filter_func=None):
    """Generate a unique URL"""
    if not filter_func:
        from models.post import Post
        filter_func = lambda url: Post.query().filter(Post.url == url).get()
    
    p = filter_func(url)
    if not p:
        return url
    
    genter = (i for i in range(1, 1000))
    
    if url.find("/") != -1:
        if url.split("/")[-1].find(".") != -1:
            ori, ext = url[:url.rfind(".")], url[url.rfind("."):]
        else:
            ori, ext = url[:url.rfind("/")], url[url.rfind("/"):]
    elif url.find(".") != -1:
        ori, ext = url[:url.rfind(".")], url[url.rfind("."):]
    else:
        ori, ext = url, ""
    
    while filter_func(url):
        url = f"{ori}{next(genter)}{ext}"
    
    return url

def format_time(dt, format=None):
    """Format a datetime object"""
    if not dt:
        return ""
    
    if not format:
        format = config.DATETIME_FORMAT
    
    return dt.strftime(format)

def parse_time(dtstr, format="%Y/%m/%d %H:%M:%S"):
    """Parse a datetime string"""
    return datetime.datetime.strptime(dtstr, format)

def md5_hash(text):
    """Generate MD5 hash of text"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()
