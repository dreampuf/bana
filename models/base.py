#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Base model for Bana
# Author: dreampuf (original), updated by Codegen

from google.cloud import ndb
import hashlib
import pickle
import logging

# Constants
TABLE_COUNT_TAG_PRE = "tablecount"

class Setting(ndb.Model):
    """Settings model for storing configuration values"""
    name = ndb.StringProperty()
    value = ndb.TextProperty()
    
    _settingcache = {}
    
    @classmethod
    def get(cls, name, default=None, useMemoryCache=True):
        """Get a setting value by name"""
        from google.cloud import ndb
        
        # Check memory cache
        if useMemoryCache and name in cls._settingcache:
            return cls._settingcache[name]
        
        # Check memcache
        client = ndb.Client()
        with client.context():
            # Try to get from datastore
            try:
                opt = cls.get_by_id(name)
                if opt:
                    result = pickle.loads(opt.value.encode('utf-8'))
                    
                    if isinstance(result, str):
                        result = result.encode("utf-8")
                    
                    if useMemoryCache:
                        cls._settingcache[name] = result
                    
                    return result
            except Exception as e:
                logging.error(f"Error getting setting {name}: {e}")
                
            return default
    
    @classmethod
    def set(cls, name, value, useMemoryCache=True):
        """Set a setting value"""
        from google.cloud import ndb
        
        # Update memory cache
        if useMemoryCache:
            cls._settingcache[name] = value
        
        # Update datastore
        client = ndb.Client()
        with client.context():
            opt = cls.get_or_insert(name)
            opt.name = name
            opt.value = pickle.dumps(value).decode('latin1')
            opt.put()
    
    @classmethod
    def remove(cls, name):
        """Remove a setting"""
        from google.cloud import ndb
        
        # Remove from memory cache
        if name in cls._settingcache:
            del cls._settingcache[name]
        
        # Remove from datastore
        client = ndb.Client()
        with client.context():
            opt = cls.get_by_id(name)
            if opt:
                opt.key.delete()

class ConfigProperty:
    """Property descriptor for configuration values"""
    
    def __init__(self, name, default=None, useMemoryCache=True):
        self.name = f"config_{name}"
        self.default = default
        self.usememorycache = useMemoryCache
    
    def __get__(self, instance, klass):
        return Setting.get(self.name, self.default, self.usememorycache)
    
    def __set__(self, instance, value):
        Setting.set(self.name, value, self.usememorycache)
    
    def __str__(self):
        return str(Setting.get(self.name, self.default, self.usememorycache))

class Pager:
    """Pagination helper class"""
    
    def __init__(self, data, count, index, last):
        self.data = data
        self.count = count
        self.index = index
        self.prev = index - 1
        self.next = (index + 1 > last) and 0 or (index + 1)
        self.last = last
    
    def __repr__(self):
        return f"<Pager: count:{self.count}, index:{self.index}, prev:{self.prev}, next:{self.next}, last:{self.last}, Entry_Type:{self.data[0].__class__.__name__ if self.data else 'None'}>"

def func2str(func):
    """Generate a hash for a function"""
    import inspect
    code = inspect.getsource(func)
    return hashlib.md5(code.encode('utf-8')).hexdigest()

class BaseModel(ndb.Model):
    """Base model with common functionality"""
    
    def put(self, **kwargs):
        """Override put to update counter"""
        if not self.key:
            tname = f"{TABLE_COUNT_TAG_PRE}_{self.__class__.__name__}"
            tval = Setting.get(tname, useMemoryCache=False)
            if tval is None:
                tval = self.__class__.total()
            Setting.set(tname, tval + 1, False)
        return super().put(**kwargs)
    
    def delete(self, **kwargs):
        """Override delete to update counter"""
        if self.key:
            tname = f"{TABLE_COUNT_TAG_PRE}_{self.__class__.__name__}"
            tval = Setting.get(tname, useMemoryCache=False)
            if tval is None:
                tval = self.__class__.total()
            Setting.set(tname, tval - 1, False)
        return self.key.delete()
    
    @classmethod
    def puts(cls, entities):
        """Batch put entities"""
        tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}"
        Setting.set(tname, cls.total() + len(entities), False)
        ndb.put_multi(entities)
    
    @classmethod
    def deletes(cls, keys):
        """Batch delete entities"""
        tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}"
        Setting.set(tname, cls.total() - len(keys), False)
        ndb.delete_multi(keys)
    
    @classmethod
    def fetch_page(cls, p, plen=20, query_func=None, realtime_count=False):
        """Fetch a page of entities"""
        total = cls.total(query_func, realtime_count=realtime_count)
        n = total // plen
        if total % plen != 0:
            n = n + 1
        
        if p < 0 or p > n:
            p = 1
        
        offset = (p - 1) * plen
        query = cls.query()
        
        if query_func:
            query = query_func(query)
        
        results = query.fetch(plen, offset=offset)
        
        return Pager(results, total, p, n)
    
    @classmethod
    def cursorfetch(cls, cursor, plen=20, query_func=None):
        """Fetch entities using a cursor"""
        query = cls.query()
        
        if query_func:
            query = query_func(query)
        
        if cursor:
            query = query.start_cursor(cursor)
        
        results, next_cursor, more = query.fetch_page(plen)
        
        return results, next_cursor
    
    @classmethod
    def total(cls, query_func=None, realtime_count=False):
        """Get total count of entities"""
        if realtime_count:
            query = cls.query()
            if query_func:
                query = query_func(query)
            return query.count()
        
        if query_func:
            tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}::{func2str(query_func)}"
        else:
            tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}"
        
        tval = Setting.get(tname, useMemoryCache=False)
        if tval is None:
            logging.info(f"Calculating the {cls.__name__} total count")
            query = cls.query()
            if query_func:
                query = query_func(query)
            tval = query.count()
            Setting.set(tname, tval, False)
        
        return tval
    
    @classmethod
    def refresh_total(cls, query_func=None):
        """Refresh the total count"""
        if query_func:
            tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}::{func2str(query_func)}"
        else:
            tname = f"{TABLE_COUNT_TAG_PRE}_{cls.__name__}"
        
        query = cls.query()
        if query_func:
            query = query_func(query)
        
        tval = query.count()
        Setting.set(tname, tval, False)
