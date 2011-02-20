#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: setting 
# author: dreampuf

from cache import memcache

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
        return Model.Setting.getValue(self.name, self.default, self.usememorycache)

    def __set__(self, instance, value):
        Model.Setting.setValue(self.name, value, self.usememorycache)



