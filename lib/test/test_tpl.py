#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: test_for template lib 
# author: dreampuf

import sys, os, unittest, logging, time

map(sys.stdout.write, sys.path)

import tenjin #import Template, Engine, gae
import tenjin.gae; tenjin.gae.init()
from tenjin.helpers import escape, to_str
#from common import tplengin, escape, to_str


class Template_Test(unittest.TestCase):

    def setUp(self):
        self.tpl = """
I'm is a mem tpl.
hello #{ name }
"""

    def test_tenjinMemLoader(self):
        a = tenjin.Template(filename="afn", input=self.tpl)
        engine = tenjin.Engine(cache=tenjin.MemoryCacheStorage(), preprocess=True)
        engine.add_template(a)

        logging.info(engine.render("afn", {"name": "Dreampuf"})) 

