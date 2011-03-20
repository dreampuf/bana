#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: blog_views 
# author: dreampuf

import os, sys, logging
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from django.dispatch import dispatcher

from config import config
from model import Post, PostSignals, Key
from common import BlogHandler

INDEXPOSTFILTER = lambda x:x.order("-created")

def rtotal_Index(*args, **kw):
    Post.refresh_total(func=INDEXPOSTFILTER)

dispatcher.connect(rtotal_Index, signal=PostSignals.New)

class IndexHandler(BlogHandler):
    def get(self):
        p = self.GET.get("p")
        p = int(p) if p and p.isdigit() else 1
        pager = Post.fetch_page(p, func=INDEXPOSTFILTER)
        logging.info(pager.count)

        context = {"pager": pager}

        self.render("index.html", context)

class CategoryHandler(BlogHandler):
    def get(self, category_key_name):
        p = self.GET.get("p")
        p = int(p) if p and p.isdigit() else 1
        
        cate = Key.from_path("Category", category_key_name)
        if not cate:
            #TODO 404
            pass

        pager = Post.fetch_page(p, func=lambda x:x.filter("category =", cate).order("-created"))

        context = {"pager": pager}
        self.render("index.html", context)

class ViewHandler(BlogHandler): # 大苦逼处理类
    def get(self, path):
        p = Post.get_by_path(path)
        if p:
            context = {"post": p}
            self.render("archive.html", context)
