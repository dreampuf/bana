#! /usr/bin/env python
# -*- coding: utf-8 -*-
# discription: test_lib 
# author: dreampuf


import os, unittest, logging, time
import string, random

from google.appengine.ext import db

from lib.model import BaseModel


## Test for BaseModel #######

class TempTable(BaseModel):
    tkey = db.IntegerProperty(default=0)
    value = db.StringProperty()
    create = db.DateTimeProperty(auto_now_add=True)

class BaseModelTest(unittest.TestCase):
    def setUp(self):

        for i in TempTable.all():
            i.delete()

        #init data
        ls = []
        for i in xrange(500):
            ls.append(TempTable(tkey=i, value=random.choice(string.lowercase)))
        db.put(ls)

    def dearDown(self):
        for i in TempTable.all():
            i.delete()
        logging.info("被执行拉")
        
    def testFetch(self):
        index = 1 
        ls = TempTable.fetch_page(index, 20)
        logging.info(ls)
        for n, i in enumerate(ls.data):
            self.assertEquals(i.tkey, n)

        cursor = TempTable.cursor()
        self.assertTrue(not cursor is None)
        logging.info(cursor)
        
        self.assertEquals(TempTable.fetch_page(10).data[0].tkey, 180)

        als = TempTable.cursorfetch(cursor)
        for n, i in enumerate(als):
            self.assertEquals(i.tkey, ls.data[n].tkey + 20)


    def testPut(self):
        befor = TempTable.total()
        i = TempTable(tkey=9527, value=random.choice(string.lowercase))
        i.put()
        self.assertEquals(befor + 1, TempTable.total())

    def testDelete(self):
        befor = TempTable.total()
        i = TempTable.fetch_page(1, 1)
        i.data[0].delete() 
        self.assertEquals(befor - 1, TempTable.total())




