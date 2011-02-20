#! /usr/bin/env python
# -*- coding: utf-8 -*-
# discription: cache 
# author: dreampuf

import time
from datetime import datetime
from google.appengine.api import memcache

class BaseCache(object):
    def __init__(self, timeout=0):
        try:
            timeout = int(timeout)
        except (ValueError, TypeError):
            timeout = 0
        self.default_timeout = timeout

    def get(self, key, default=None):
        raise NotImplementedError

    def set(self, key, value, timeout=None):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError

    def incr(self, key, timeout=None):
        val = self.get(key)
        if val:
            val = val + 1
            self.set(key, val, timeout)

    def decr(self, key, timeout=None):
        val = self.get(key)
        if val:
            val = val - 1
            self.set(key, val, timeout)

    def get_many(self, keys):
        d = {}
        for k in keys:
            val = self.get(k)
            if val is not None:
                d[k] = val
        return d

    def has_key(self, key):
        return self.get(key) is not None

    def __contains__(self, key):
        return self.has_key(key)

def dict_cmp(x, y):
    return 1 if x[1] > y[1] else \
           0 if x[1] == y[1] else \
           -1

class LocalCache(BaseCache):
    def __init__(self, cull_frequency=3, max_entrys=300, *args, **kw):
        self._cache = {}
        self._expire = {} 
        self._cull_frequency = cull_frequency
        self.max_entrys = max_entrys
        super(LocalCache, self).__init__(*args, **kw)
        
    def get(self, key, default=None):
        if self._expire.has_key(key):
            if time.time() > self._expire[key]:
                self.delete(key)
                return default
            return self._cache.get(key, default)
        else:
            return default

    def set(self, key, val, timeout=None):
        self._cull()
        timeout = self.default_timeout if timeout is None else timeout
        self._cache[key] = val
        self._expire[key] = time.time() + timeout

    def delete(self, key):
        #if self._cache.has_key(kddey):
        #    del self._cache[key]
        self._expire.pop(key, None)
        self._cache.pop(key, None)
        

    def has_key(self, key):
        exp = self._expire.get(key, None) 
        if exp is None:
            return False
        elif exp > time.time():
            return True

        self._expire.pop(key, None)
        self._cache.pop(key,None)

    def _cull(self):
        clen = len(self._cache)
        if clen > self.max_entrys:
            if self._cull_frequency in (0, 1):
                self._cache.clear()
                self._expire.clear()
            else:
                sorted_list = sorted(self._expire.items(), dict_cmp)
                delete_count = clen/self._cull_frequency
                for i in xrange(delete_count):
                    self._cache.pop(sorted_list[i][0], None)
                    self._expire,pop(sorted_list[i][0], None)
                    
locache = LocalCache(timeout=300) 

class MemCache(BaseCache):
    default_namespace = None
    def __init__(self, default_namespace=None, *args, **kw):
        self.namespace = default_namespace if not default_namespace is None else MemCache.default_namespace
        
        super(MemCache, self).__init__(self, *args, **kw)

    def get(self, key, default=None, namespace=None):
        namespace = self.namespace if namespace is None else namespace
        ret = memcache.get(key, namespace=namespace)
        if ret is None:
            return default
        return ret

    def get_multi(self, keys, key_prefix="", namespace=None):
        namespace = self.namespace if namespace is None else namespace
        return memcache.get_multi(keys, key_prefix, namespace)

    def set(self, key, val, timeout=None, namespace=None):
        namespace = self.namespace if namespace is None else namespace
        timeout = self.default_timeout if timeout is None else timeout
        return memcache.set(key, val, timeout, namespace=namespace)

    def set_multi(self, mapping, timeout=None, key_prefix="", namespace=None): 
        namespace = self.namespace if namespace is None else namespace
        timeout = self.default_timeout if timeout is None else timeout
        return memcache.set_multi(mapping, timeout, key_prefix, namespace=namespace)

    def delete(self, key, namespace=None):
        namespace = self.namespace if namespace is None else namespace
        return memcache.delete(key, namespace=namespace)

    def delete_multi(self, keys, key_prefix="", namespace=None):
        namespace = self.namespace if namespace is None else namespace
        return memcache.delete_multi(keys, key_prefix=key_prefix, namespace=namespace)

    def get_many(self, keys, namespace=None):
        return self.get_multi(keys, namespace=namespace)

    def incr(self, key, delta=1, namespace=None, initial_value=None):
        namespace = self.namespace if namespace is None else namespace
        return memcache.incr(key, delta, namespace, initial_value)

    def decr(self, key, delta=1, namespace=None, initial_value=None):
        namespace = self.namespace if namespace is None else namespace
        return memcache.decr(key, delta, namespace, initial_value)

memcache = MemCache()





