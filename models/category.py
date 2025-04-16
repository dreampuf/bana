#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Category model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
from models.base import BaseModel

class Category(BaseModel):
    """Category model for blog post categorization"""
    ishidden = ndb.BooleanProperty(default=False)
    
    title = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    order = ndb.IntegerProperty(default=0)
    belong = ndb.KeyProperty(kind='Category')
    
    @classmethod
    def get_all(cls):
        """Get all categories ordered by order"""
        return cls.query().order(cls.order)
    
    @classmethod
    def get_categories(cls):
        """Get categories for display"""
        cates = cls.get_all().fetch()
        return [{"url": f"/category/{i.key.id()}/", "title": i.title} for i in cates]
    
    @classmethod
    def new(cls, url, title, description, order=0, belong=None):
        """Create a new category"""
        c = cls(
            id=url,
            title=title,
            description=description,
            order=order,
            belong=belong
        )
        c.put()
        return c.key
    
    @classmethod
    def keyname(cls, ckey):
        """Get category by key name"""
        return cls.get_by_id(ckey)
