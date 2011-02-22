#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: setting 
# author: dreampuf

import logging
from cache import memcache
from model import Setting

class CommentStatus(object):
    DISENABLE = "disenable"
    ENABLE = "enable"
    USERONLY = "useronly"

class _ConfigProperty(Event):

    def __init__(self, name, default=None, useMemoryCache=True):
        self.name = "config_%s" % name
        self.default= default
        self.usememorycache = useMemoryCache

    def __get__(self, instance, klass):
        return Setting.get(self.name, self.default, self.usememorycache)

    def __set__(self, instance, value):
        Setting.set(self.name, value, self.usememorycache)



