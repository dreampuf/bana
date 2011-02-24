#! /usr/bin/env python
# -*- coding: utf-8 -*-
# discription: test_lib 
# author: dreampuf


import os, unittest, logging, time


from cache import LocalCache, MemCache, CacheProperty
from docutils.core import publish_parts
from google.appengine.api import urlfetch
from lib import config

class CacheTest(unittest.TestCase):

    def test_locache(self):
        acache = LocalCache(timeout=5)

        self.assertEquals(None, acache.get("key"))

        acache.set("key", "value")
        self.assertEquals("value", acache.get("key"))

        time.sleep(5)
        self.assertEquals(None, acache.get("key"))

        acache.set("akey", "avalue", timeout=2)
        self.assertEquals("avalue", acache.get("akey"))
        time.sleep(2)
        self.assertEquals(None, acache.get("akey"))
        
        acache = LocalCache(timeout=300)
        for i in xrange(500):
            acache.set("%03d" % i, "%03d")

        end = start = -1
        for i in xrange(500, 0, -1):
            if acache.get("%03d" % i):
                end = i
                break

        for i in xrange(500):
            if acache.get("%03d" % i):
                start = i
                break

        self.assertTrue((end-start) < 300)

    def test_memcache(self):
        amcache = MemCache()
        bmcache = MemCache(default_namespace="b")

        val = time.time()
        amcache.set("key", val)
        self.assertNotEquals(amcache.get("key"), bmcache.get("key"))
        self.assertEquals(None, bmcache.get("key"))

    def test_cacheproperty(self):
        class aClass(object):
            @CacheProperty
            def a(self):
                return time.time()
        
        a = aClass()
        self.assertEquals(a.a, a.a)
        self.assertTrue(a.__dict__.has_key("a"))


class DocutilsTest(unittest.TestCase):

    def setUp(self):
        self.override_setting={
                'file_insertion_enabled':0,
                'raw_enabled':0,
                '_disable_config':1,
                }
        
        self.doc = """
===========
你好周杰伦
===========

:author:Dreampuf
:date:2011-02-14 01:38:34

谢谢
---------

#. verynice
#. yeah

是的吗?
=======

""很明显是的""

"""

    def testRST2HTML(self):
        dd = publish_parts(self.doc,writer_name='html',settings_overrides=self.override_setting)
        #logging.info(dd.keys())
        #logging.info(dd["body"])
        self.assertTrue(dd["body"].find(u"<h1>谢谢</h1>") != -1)
        self.assertTrue(dd["body"].find(u"<h2>是的吗?</h2>") != -1)



class ConfigTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_config(self):
        self.assertTrue(not config.CURPATH is None)
        #logging.info(config.CURPATH)


class AppEngineAPITest(unittest.TestCase):
    
    def test_urlfetch(self):
        #response = urlfetch.fetch('http://www.google.com')
        #self.assertEquals(15, response.content.find('<html>'))
        #logging.info(response.content)
        pass

