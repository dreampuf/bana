#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: common 
# author: dreampuf

import cgi, os, logging, sys
import datetime
import wsgiref.handlers

from google.appengine.api import memcache
from google.appengine.ext import deferred

from config 
#from config import CURPATH
import tenjin
tenjin.gae.init()
#from tenjin.helpers import escape, to_str
escape , to_str = tenjin.helpers.escape, tenjin.helpers.to_str

pjoin = os.path.join

tplengine = tenjin.Engine(path=[pjoin("static", "views")], cache=tenjin.MemoryCacheStorage(), preprocess=True)  

ZERO_TIME_DELTA = datetime.timedelta(0)
class LocalTimezone(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=Config.localtimezone)

    def dst(self, dt):
        return ZERO_TIME_DELTA

LOCAL_TIMEZONE = LocalTimezone()

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA
UTC = UTC()

def ParserTime(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return datetime.datetime.strptime(dtstr, format)

def ParserLocalTimeToUTC(dtstr, format = "%Y/%m/%d %H:%M:%S"):
    return ParserTime(dtstr, format).replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC) \
                .replace(tzinfo=None) #fix in Google Engine App


def LocalToUTC(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=LOCAL_TIMEZONE).astimezone(UTC)

def UTCtoLocal(dt):
    if dt.tzinfo:
        dt.replace(tzinfo=None)
    return dt.replace(tzinfo=UTC).astimezone(LOCAL_TIMEZONE) \
                .replace(tzinfo=None) #fix in Google Engine App

def memcached(key, cache_time=0, key_suffix_calc_func=None, namespace=None):
    def wrap(func):
        def cached_func(*args, **kw):
            key_with_suffix = key
            if key_suffix_calc_func:
                key_suffix = key_suffix_calc_func(*args, **kw)
                if key_suffix is not None:
                    key_with_suffix = '%s:%s' % (key, key_suffix)

            value = memcache.get(key_with_suffix, namespace)
            if value is None:
                value = func(*args, **kw)
                try:
                    memcache.set(key_with_suffix, value, cache_time, namespace)
                except:
                    pass
            return value
        return cached_func
    return wrap


