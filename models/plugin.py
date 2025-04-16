#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Plugin model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
from models.base import BaseModel

class Plugin(BaseModel):
    """Plugin model for blog plugins"""
    enable = ndb.BooleanProperty(default=False)
    
    pluginguid = ndb.StringProperty()
    pluginname = ndb.StringProperty()
    plugintype = ndb.StringProperty()
    plugindescription = ndb.StringProperty()
    pluginauthor = ndb.StringProperty()
    pluginurl = ndb.StringProperty()
    pluginsize = ndb.IntegerProperty(default=0)
    plugindata = ndb.BlobProperty()
