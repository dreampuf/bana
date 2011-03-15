#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_views 
# author: dreampuf

import logging

from config import config
from common import BlogHandler, AdminHandler

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

        self.render("admin_post_new.html", context)

    def post(self):
        logging.info(self.request.POST)




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
                if isinstance(getattr(config, key), list) and val.find("\n") != -1:
                    setattr(config, key, val.split("\n")) 
                else:
                    setattr(config, key, val)
                pass
            except AttributeError, ex:
                continue

        self.redirect(".")









