#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: blog_views 
# author: dreampuf

import logging

from config import config
from model import Post
from common import BlogHandler

class IndexHandler(BlogHandler):
    def get(self):
        p = self.GET.get("p")
        p = int(p) if p and p.isdigit() else 1
        pager = Post.fetch_page(p)

        context = {"pager": pager}

        self.render("index.html", context)

class ViewHandler(BlogHandler): # 大苦逼处理类
    def get(self, path):
        p = Post.get_by_path(path)
        if p:
            context = {"post": p}
            self.render("archive.html", context)
