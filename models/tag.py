#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Tag model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
from models.base import BaseModel

class Tag(BaseModel):
    """Tag model for blog post tagging"""
    # key_name as title
    count = ndb.IntegerProperty(default=1)
    
    @property
    def posts(self):
        """Get posts with this tag"""
        from models.post import Post
        return Post.query().filter(Post.tags == self.key.id())
    
    @classmethod
    def incr(cls, tag):
        """Increment tag count"""
        t = cls.get_by_id(tag)
        if not t:
            t = cls(id=tag)
            t.put()
        else:
            t.count += 1
            t.put()
    
    @classmethod
    def decr(cls, tag):
        """Decrement tag count"""
        t = cls.get_by_id(tag)
        if t:
            if t.count == 1:
                t.key.delete()
            else:
                t.count -= 1
                t.put()
