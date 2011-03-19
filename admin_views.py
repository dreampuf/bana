#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_views 
# author: dreampuf

import logging

from config import config
from common import BlogHandler, AdminHandler, randstr, json, realurl 
from model import run_in_transaction, Rollback, Category, Post, Tag

class LoginHandler(BlogHandler):
    def get(self):
        self.render("login.html", 
                   { "page_name": u"管理员登录",
                    
                    }) 


    def post(self):
        self.redirect(config.ADMINURL)


class AdminIndexHandler(AdminHandler):
    def get(self):
        
        self.render("admin_page.html", { "page_name": u"站点管理",
                                         "page_title": u"基本信息", })

class AdminCategoryHandler(AdminHandler):

    def post(self):
        logging.info(self.request.POST)
        self.set_content_type('json')
        pdict = self.request.POST
        action = pdict.get("action", "")
        
        if action == "new":
            try:
                Category.new(pdict.get("category.url", randstr()),
                             pdict.get("category.title"),
                             pdict.get("category.discription") )
                Category.refresh_total()
            except Rollback, ex:
                self.jsonout(ex)
            else:
                self.jsonout("ok")

class AdminPostHandler(AdminHandler):
    def get(self):
        p = self.GET.get("p")
        p = int(p) if p and p.isdigit() else 1
        pager = Post.fetch_page(p)

        context = {"page_name": u"文章管理",
                   "page_title": u"文章管理",
                   "pager": pager }
        self.render("admin_post.html", context)

class AdminModifyPostHandler(AdminHandler):
    def get(self, post_id):
        p = Post.get_by_id(int(post_id)) if post_id.isdigit() else None
        if not p:
            self.redirect(config.BLOG_ADMIN_PATH + "post/")
            return
        
        context = {"page_name": u"编辑文章",
                   "page_title": u"编辑文章",
                   "all_category": Category.get_all(),

                   "post.title": p.title,
                   "post.category": p.category.key().name(),
                   "post.url": p.url,
                   "post.tags": ",".join(p.tags),
                   "post.keyword": ",".join(p.keyword),
                   "post.content": p.content, }
        self.render("admin_post_editor.html", context)

    def post(self, post_id):
        post_id = int(post_id)
        p = Post.id(post_id)
        if not p:
            self.redirect(config.BLOG_ADMIN_PATH + "post/")
            return
        pdict = self.request.POST

        cur_tags = set(pdict.get("post.tags").split(","))
        old_tags = set(p.tags)
        for i in old_tags^(cur_tags&old_tags):
            Tag.Decr(i)
        for i in cur_tags^(cur_tags&old_tags):
            Tag.Incr(i)
        tags = list(cur_tags)

        try:
            p = Post.modify(post_id=post_id,
                            title=pdict.get("post.title"),
                            category_keyname=pdict.get("post.category"),
                            author_keyname=self.session.get("curr_ukey"),
                            url=pdict.get("post.url"),
                            keyword=pdict.get("post.keyword").split(","),
                            tags=pdict.get("post.tags").split(","),#tags,
                            content=pdict.get("post.content"),
                            format=pdict.get("post.format") )
            p.realurl = realurl(p)
            p.put()
        except Exception, ex:
            logging.info(ex)
            context = {}
            context.update(self.request.POST)
            context["errors_msg"] = ex
            context["page_name"] = u"修改文章"
            context["page_title"] = u"修改文章" 
            context["all_category"] = Category.get_all()
            self.render("admin_post_editor.html", context)
        else:
            self.redirect(config.BLOG_ADMIN_PATH + "post/")

class AdminAddPostHandler(AdminHandler):
    def get(self):
        editor = self.GET.get("editor")
        if editor and editor in config.EDITOR_TYPE :
            config.POST_EDITOR = editor 
        context = {}
#        config.POST_EDITOR = ""
        editor = config.POST_EDITOR

        if not editor.strip(): #首次编辑, 选择编辑器
            context["page_name"] = u"编辑器选择"
            context["page_title"] = u"首次编辑文章,请选择你所喜爱的文本编辑"
            context["first"] = True
        else:
            context["page_name"] = u"添加文章"
            context["page_title"] = u"添加文章" 
            context["all_category"] = Category.get_all()

        self.render("admin_post_editor.html", context)

    def post(self):
        pdict = self.request.POST
        
        try:
            #def new(cls, title, category_keyname, author_keyname, url, keyword, tags, content, status=PostStatus.NORMAL, format=PostFormat.PLAIN, enablecomment=True):
            tags = pdict.get("post.tags").split(",")
            for i in tags:
                Tag.Incr(i)

            p = Post.new(title=pdict.get("post.title"),
                         category_keyname=pdict.get("post.category"),
                         author_keyname=self.session.get("curr_ukey"),
                         url=pdict.get("post.url"),
                         keyword=pdict.get("post.keyword").split(","),
                         tags=tags,
                         content=pdict.get("post.content"),
                         format=pdict.get("post.format") )
            p.realurl = realurl(p)
            p.put()
            Post.refresh_total()

        except Exception, ex:
            context = {}
            context.update(self.request.POST)
            context["errors_msg"] = ex
            context["page_name"] = u"添加文章"
            context["page_title"] = u"添加文章" 
            context["all_category"] = Category.get_all()
            self.render("admin_post_editor.html", context)
        else:
            self.redirect(config.BLOG_ADMIN_PATH + "post/")
            

class AdminConfigHandler(AdminHandler):
    def get(self):
        
        context = {"page_title": u"站点设置", }
        self.render("admin_config.html", context)

    def post(self):

        post_editor = self.request.POST.get("POSTEDITOR")#pop("POST_EDITOR")
        if post_editor in config.EDITOR_TYPE:
            config.POST_EDITOR = post_editor

        for key, val in self.request.POST.items():
            try:
                if isinstance(getattr(config, key), list):
                    if val.find("\n") != -1:
                        setattr(config, key, val.split("\n")) 
                    else:
                        setattr(config, key, [val])
                else:
                    setattr(config, key, val)
                pass
            except AttributeError, ex:
                continue

        self.redirect(".")









