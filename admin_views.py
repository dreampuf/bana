#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_views 
# author: dreampuf

import logging

import config
from common import BlogHandler, AdminHandler

class LoginHandler(BlogHandler):
    def get(self):
        self.render("login.html", 
                { 
                    "page_name": u"管理员登录",
                    
                    }) 


    def post(self):
        self.redirect(config.ADMINURL)


class AdminIndexHandler(AdminHandler):
    def get(self):
        
        self.render("index.html",
                {
                    "page_name": u"站点管理",
                    })
