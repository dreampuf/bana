#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Post model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
import logging
from models.base import BaseModel
from models.tag import Tag

class PostStatus:
    """Post status constants"""
    NORMAL = 0
    HIDDEN = 1
    TOP = 2
    PAGE = 3

class PostFormat:
    """Post format constants"""
    PLAIN = "html"
    MARKDOWN = "markdown"
    RST = "rest"
    UBB = "bbcode"

class PostSignals:
    """Post signal constants"""
    New = "Post.New"
    Modify = "Post.Modify"

class Post(BaseModel):
    """Post model for blog posts"""
    status = ndb.IntegerProperty(default=PostStatus.NORMAL)
    enablecomment = ndb.BooleanProperty(default=True)
    format = ndb.StringProperty(default=PostFormat.PLAIN, indexed=False)
    realurl = ndb.StringProperty(default="")
    
    category = ndb.KeyProperty(kind='Category')
    author = ndb.KeyProperty(kind='User')
    title = ndb.StringProperty()
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    date_modify = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty()
    keyword = ndb.StringProperty(repeated=True)
    content = ndb.TextProperty()
    views = ndb.IntegerProperty(default=0)
    
    tags = ndb.StringProperty(repeated=True)
    
    @classmethod
    def new(cls, title, category_keyname, author_keyname, url, keyword, tags, content, 
            status=PostStatus.NORMAL, format=PostFormat.PLAIN, enablecomment=True):
        """Create a new post"""
        from models.category import Category
        from models.user import User
        
        # Get category and author keys
        category = Category.get_by_id(category_keyname).key if category_keyname else None
        author = User.get_by_id(author_keyname).key if author_keyname else None
        
        # Create post
        p = cls(
            title=title,
            category=category,
            author=author,
            url=url,
            keyword=keyword,
            tags=tags,
            content=content,
            format=format,
            enablecomment=enablecomment,
            status=status
        )
        
        # Update tags
        for tag in tags:
            Tag.incr(tag)
        
        # Save post
        key = p.put()
        
        # Generate real URL
        p.realurl = cls._generate_realurl(p)
        p.put()
        
        # Send signal (using Cloud Tasks or Pub/Sub in a real implementation)
        logging.info(f"New post created: {title}")
        
        return key
    
    @classmethod
    def modify(cls, post_id, title, category_keyname, author_keyname, url, keyword, tags, content,
              status=PostStatus.NORMAL, format=PostFormat.PLAIN, enablecomment=True):
        """Modify an existing post"""
        from models.category import Category
        from models.user import User
        
        # Get post
        p = cls.get_by_id(post_id)
        if not p:
            return None
        
        # Update tags
        old_tags = set(p.tags)
        new_tags = set(tags)
        
        # Remove tags that are no longer used
        for tag in old_tags - new_tags:
            Tag.decr(tag)
        
        # Add new tags
        for tag in new_tags - old_tags:
            Tag.incr(tag)
        
        # Get category and author keys
        category = Category.get_by_id(category_keyname).key if category_keyname else None
        author = User.get_by_id(author_keyname).key if author_keyname else None
        
        # Update post
        p.title = title
        p.category = category
        p.author = author
        p.url = url
        p.keyword = keyword
        p.tags = tags
        p.content = content
        p.format = format
        p.enablecomment = enablecomment
        p.status = status
        
        # Save post
        key = p.put()
        
        # Generate real URL if needed
        if not p.realurl:
            p.realurl = cls._generate_realurl(p)
            p.put()
        
        # Send signal (using Cloud Tasks or Pub/Sub in a real implementation)
        logging.info(f"Post modified: {title}")
        
        return key
    
    @classmethod
    def get_by_path(cls, path, keys_only=False):
        """Get post by path"""
        query = cls.query().filter(cls.realurl == path)
        if keys_only:
            query = query.keys_only()
        return query.get()
    
    @classmethod
    def get_feed_post(cls, feed_count=20):
        """Get posts for feed"""
        return cls.query().filter(cls.status == PostStatus.NORMAL).order(-cls.date_created).fetch(feed_count)
    
    @staticmethod
    def _generate_realurl(post):
        """Generate a real URL for a post"""
        # This would implement the URL generation logic based on the post properties
        # For now, just return the URL as is
        return post.url
