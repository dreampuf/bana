#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_views 
# author: dreampuf

import logging
from common import BlogHandler, AdminHandler

class LoginHandler(BlogHandler):
    def get(self):
        self.render("login.html", {"page_name": u"管理员登录" }) 


    def post(self):
        pass


class AdminIndexHandler(AdminHandler):
    def get(self):
        pass
