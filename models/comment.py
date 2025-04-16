#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Comment model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
import logging
from models.base import BaseModel

class CommentType:
    """Comment type constants"""
    COMMENT = "comment"
    TRACKBACK = "trackback"
    PINGBACK = "pingback"

class CommentSignals:
    """Comment signal constants"""
    New = "Comment.New"

class Comment(BaseModel):
    """Comment model for blog post comments"""
    commenttype = ndb.StringProperty(default=CommentType.COMMENT)
    
    belong = ndb.KeyProperty(kind='Post')
    re = ndb.KeyProperty(kind='Comment')
    content = ndb.TextProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    nickname = ndb.StringProperty()
    ip = ndb.StringProperty()
    website = ndb.StringProperty()
    email = ndb.StringProperty()
    hascheck = ndb.BooleanProperty(default=True)
    
    @classmethod
    def new(cls, belong, nickname, email, re=None, ip=None, website=None, content=None, 
            hascheck=True, commenttype=CommentType.COMMENT):
        """Create a new comment"""
        # Create comment
        c = cls(
            parent=belong,
            belong=belong,
            nickname=nickname,
            email=email,
            re=re,
            ip=ip or "",
            website=website,
            content=content or "",
            hascheck=hascheck,
            commenttype=commenttype
        )
        
        # Save comment
        key = c.put()
        
        # Send signal (using Cloud Tasks or Pub/Sub in a real implementation)
        logging.info(f"New comment created by {nickname}")
        
        return key
    
    @classmethod
    def by_post(cls, post, plen=50, cursor=None):
        """Get comments for a post"""
        query = cls.query(ancestor=post)
        
        if cursor:
            query = query.start_cursor(cursor)
        
        results, next_cursor, more = query.fetch_page(plen)
        
        return results, next_cursor
