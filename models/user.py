#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# User model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
import hashlib
import logging
import traceback
from models.base import BaseModel

class User(BaseModel):
    """User model for authentication and user management"""
    nickname = ndb.StringProperty(required=True)
    password = ndb.StringProperty(indexed=False)
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    
    lastip = ndb.StringProperty(indexed=False)
    lastlogin = ndb.DateTimeProperty()
    
    @classmethod
    def check(cls, email, password):
        """Check user credentials"""
        try:
            user = cls.get_by_id(email)
            if user and password and user.password == hashlib.md5(password.encode('utf-8')).hexdigest():
                return user
            return None
        except Exception:
            logging.error(traceback.format_exc())
            return None
    
    @classmethod
    def by_email(cls, email):
        """Get user by email"""
        return cls.get_by_id(email)
