#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Attachment model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
import os
from models.base import BaseModel

class Attachment(BaseModel):
    """Attachment model for file uploads"""
    beuse = ndb.KeyProperty(kind='Post')
    belong = ndb.KeyProperty(kind='User')
    
    filename = ndb.StringProperty()
    filetype = ndb.StringProperty()
    filesize = ndb.IntegerProperty(default=0)
    content = ndb.BlobProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    
    def set_filetype(self, filename):
        """Set file type based on filename extension"""
        self.filetype = os.path.splitext(filename)[1][1:]
