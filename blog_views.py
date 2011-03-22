#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: blog_views 
# author: dreampuf

import os, sys, logging, traceback
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from django.dispatch import dispatcher

from config import config
from model import Post
from model import PostSignals
from model import Key 
from model import User 
from model import Comment 
from model import Rollback 
from common import BlogHandler, attach_event

INDEXPOSTFILTER = lambda x:x.order("-created")
def rtotal_Index(*args, **kw):
    Post.refresh_total(func=INDEXPOSTFILTER)
attach_event(func=rtotal_Index, signal=PostSignals.New)

class IndexHandler(BlogHandler):
    def get(self):
        p = self.GET.get("p")
        p = int(p) if p and p.isdigit() else 1
        pager = Post.fetch_page(p, func=INDEXPOSTFILTER)

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

class CommentHandler(BlogHandler):
    def post(self, post_id):
        post_id = int(post_id)
        post = Post.id(post_id)
        if not post:
            #TODO 404
            return
        
        pdict = self.request.POST
        
        nickname = pdict.get("author")
        email = pdict.get("email")
        website = pdict.get("url")
        comment = pdict.get("comment")
        logging.info(website)

        #def new(cls, belong, nickname, email, author=None, re=None, ip=None, website=None, hascheck=True, commenttype=CommentType.COMMENT):
        try:
            c = Comment.new(belong=post,
                            nickname=nickname,
                            email=email,
                            website=website,
                            content=comment,
                            ip=self.request.client_ip)
        except Exception, ex:
            logging.info(traceback.format_exc())

        self.redirect("/" + post.realurl)


class ViewHandler(BlogHandler): # 大苦逼处理类
    def get(self, path):
        gdict = self.GET
        post = Post.get_by_path(path)
        if post:
            n = gdict.get("n", None)
            post_comments, post_next_cursor = Comment.by_post(post, plen=3, cursor=n)
            context = {"post": post,
                       "post_comments": post_comments, 
                       "post_last_cursor": n,
                       "post_next_cursor": post_next_cursor }
            self.render("single.html", context)
            return 

        self.render("single.html", {})
