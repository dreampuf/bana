#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: blog_views 
# author: dreampuf

import os, sys, logging, traceback, urllib

CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))

from google.appengine.api import memcache
from django.dispatch import dispatcher

from config import config
from model import Post
from model import PostStatus
from model import PostSignals
from model import Key 
from model import User 
from model import Comment 
from model import CommentSignals
from model import Rollback 
from common import BlogHandler, attach_event

INDEXPOSTFILTER = lambda x:x.filter("status =", PostStatus.NORMAL).order("-date_created")
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
        
        pager = Post.fetch_page(p, 
                                func=lambda x:x.filter("category =", cate).filter("status =", PostStatus.NORMAL).order("-date_created"),
                                realtime_count=True)

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

        self.redirect("%s/%s" % (config.BASEURL, post.realurl))

def view_counter(handler):
    def view_handler(self, path):
        url = urllib.unquote(path)

        view = memcache.get("views")
        if view == None:
            view = {}
        if not url in view:
            view[url] = 0
        view[url] += 1
        memcache.set("views", view)
        return handler(self, path)
    return view_handler

VIEWCOMMENTFILTER = lambda x: x.filter("hascheck =", True).order("date_created") if config.COMMENT_NEEDLOGINED else x.order("date_created")
def rtotal_Comment(*args, **kw):
    Comment.refresh_total(func=VIEWCOMMENTFILTER)
attach_event(func=rtotal_Comment, signal=CommentSignals.New)

class ViewHandler(BlogHandler): # 大苦逼处理类
    @view_counter
    def get(self, path):
        gdict = self.GET
        path = urllib.unquote(path)
        if path == config.FEED_SRC: #FEED
            self.set_content_type("atom")
            posts = Post.get_feed_post(config.FEED_NUMBER) 
            self.render("feed.xml", {"posts": posts })
            return

        post = Post.get_by_path(path)
        if post:
            p = gdict.get("p", None)
            p = int(p) if p and p.isdigit() else 1

            def post_comment_filter(query):
                query = query.filter("belong =", post)
                if config.COMMENT_NEEDLOGINED:
                    query = query.filter("hashcheck =", True)
                query = query.order("date_created")
                return query

            post_comments = Comment.fetch_page(p, config.COMMENT_PAGE_COUNT, func=post_comment_filter, realtime_count=True)
            context = {"post": post,
                       "post_comments": post_comments, } 
            self.render("single.html", context)
            return 

        #self.render("single.html", {})
