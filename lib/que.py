#! /usr/bin/env python
# -*- coding: utf-8 -*-
# discription: WSGI 
# author: dreampuf

"""
    que modified from keakon's yui.
    original author: keakon<mailto:keakon@gmail.com>
"""

import re
import time
import logging
import cStringIO as StringIO

from datetime import datetime, timedelta
from hashlib import md5
from urlparse import urljoin, urlunsplit

from google.appengine.ext import webapp
from webob.multidict import MultiDict
from cache import memcache, locache, CacheProperty 

HTTP_STATUS = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi-Status',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Moved Temporarily',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Time-out',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Large',
    415: 'Unsupported Media Type',
    416: 'Requested range not satisfiable',
    417: 'Expectation Failed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Time-out',
    505: 'HTTP Version not supported',
    507: 'Insufficient Storage',
}



class Request(webapp.Request):
    """ a wapper with webapp.Request """

    __SPIDER_PATTERN = re.compile('(bot|crawl|spider|slurp|sohu-search|lycos|robozilla)', re.I)
    @CacheProperty
    def is_spider(self):
        return self.__SPIDER_PATTERN.search(self.user_agent) is not None

    @CacheProperty
    def is_system(self):
        return self.remote_addr[:2] == '0.'

    @CacheProperty
    def ua_details(self):
        '''
        parse browser, platform, os and vendor from user agent.

        从user agent解析浏览器、平台、操作系统和产商信息。

        @rtype: string
        @return: tuple of browser, platform, os and vendor

        browser, platform, os, vendor组成的元组
        '''
        user_agent = self.user_agent
        os = ''
        browser = ''
        platform = ''
        vendor = ''
        if user_agent:
            if 'iPhone' in user_agent:
                os = 'iOS'
                platform = 'iPhone'
                vendor = 'Apple'
            elif 'iPad' in user_agent:
                os = 'iOS'
                platform = 'iPad'
                vendor = 'Apple'
            elif 'iPod' in user_agent:
                os = 'iOS'
                platform = 'iPod'
                vendor = 'Apple'
            elif 'Android' in user_agent:
                os = platform = 'Android'
            elif 'BlackBerry' in user_agent:
                os = 'BlackBerry OS'
                platform = 'BlackBerry'
                vendor = 'RIM'
            elif 'Palm' in user_agent:
                os = 'PalmOS'
                platform = 'Palm'
            elif 'Windows Phone' in user_agent:
                os = platform = 'Windows Mobile'
            elif 'PSP' in user_agent:
                platform = 'PSP'
                vendor = 'Sony'
            elif 'Kindle' in user_agent:
                os = 'Linux'
                platform = 'Kindle'
            elif 'Nintendo' in user_agent or 'Nitro' in user_agent:
                platform = 'Wii'
                vendor = 'Nintendo'

            if not os:
                if 'Windows' in user_agent:
                    if 'Windows NT 6.1' in user_agent:
                        os = 'Windows 7'
                    elif 'Windows NT 5.1' in user_agent:
                        os = 'Windows XP'
                    elif 'Windows NT 6.0' in user_agent:
                        os = 'Windows Vista'
                    elif 'Windows NT 5.2' in user_agent:
                        os = 'Windows Server 2003'
                    elif 'Windows NT 5.0' in user_agent:
                        os = 'Windows 2000'
                    elif 'Windows CE' in user_agent:
                        os = 'Windows CE'
                    else:
                        os = 'Windows'
                elif 'Macintosh' in user_agent or 'Mac OS' in user_agent:
                    os = 'Mac OS'
                elif 'Linux' in user_agent:
                    os = 'Linux'
                elif 'FreeBSD' in user_agent:
                    os = 'FreeBSD'
                elif 'OpenBSD' in user_agent:
                    os = 'OpenBSD'
                elif 'Solaris' in user_agent:
                    os = 'Solaris'
                elif 'Symbian' in user_agent or 'SymbOS' in user_agent:
                    if 'Series60' in user_agent:
                        os = 'SymbianOS Series60'
                    elif 'Series40' in user_agent:
                        os = 'SymbianOS Series40'
                    else:
                        os = 'SymbianOS'

            if not browser:
                if 'MSIE' in user_agent:
                    browser = 'Internet Explorer'
                elif 'Firefox' in user_agent:
                    browser = 'Firefox'
                elif 'Chrome' in user_agent:
                    browser = 'Chrome'
                elif 'Safari' in user_agent:
                    if 'Mobile' in user_agent:
                        browser = 'Mobile Safari'
                        self.is_mobile = True
                    else:
                        browser = 'Safari'
                elif 'Opera Mini' in user_agent:
                    browser = 'Opera Mini'
                    self.is_mobile = True
                elif 'Opera Mobi' in user_agent:
                    browser = 'Opera Mobile'
                    self.is_mobile = True
                elif 'Opera' in user_agent:
                    browser = 'Opera'
                elif 'UCWEB' in user_agent:
                    browser = 'UCWEB'
                    self.is_mobile = True
                elif 'IEMobile' in user_agent:
                    browser = 'IEMobile'
                    self.is_mobile = True

            if not vendor:
                if 'Nokia' in user_agent:
                    vendor = 'Nokia'
                elif 'motorola' in user_agent:
                    vendor = 'Motorola'
                elif 'Sony' in user_agent:
                    vendor = 'Sony'
                elif 'samsung' in user_agent.lower():
                    vendor = 'Samsung'
        return browser, platform, os, vendor

    @CacheProperty
    def is_mobile(self):
        environ = self.environ
        if 'HTTP_X_WAP_PROFILE' in environ or 'HTTP_PROFILE' in environ or 'X-OperaMini-Features' in environ or\
            self.first_match(('application/vnd.wap.xhtml+xml', 'text/vnd.wap.wml'), ''):
            return True
        
        user_agent = self.user_agent
        if user_agent:
            user_agent_lower = user_agent.lower()
            if 'phone' in user_agent_lower or 'mobi' in user_agent_lower or 'wap' in user_agent_lower:
                return True
        
            browser, platform, os, vendor = self.ua_details
            if platform or vendor:
                return True

    @CacheProperty
    def client_ip(self):

        environ = self.environ
        ip = environ.get('HTTP_X_REAL_IP', '') # if using nginx reverse proxy
        if ip:
            return ip
        ip = environ.get('HTTP_CLIENT_IP', '')
        if ip:
            return ip
        ip = environ.get('HTTP_X_FORWARDED_FOR', '')
        if ip:
            return ip
        return environ.get('REMOTE_ADDR', 'unknown')

    def first_match(self, mime_types, fallback='text/html'):

        accept = self.accept.best_matches()
        for mime_type in mime_types:
            if mime_type in accept:
                return mime_type
        return fallback


class ResponseHeader(object):

    def __init__(self, header=None, cookie=()):

        cookie = [('Set-Cookie', value) for value in cookie]

        _header = {}
        if header:
            for name, value in header.iteritems():
                if value is not None:
                    name = self._valid_name(name)
                    if name != 'Set-Cookie':
                        _header[name] = value
                    else:
                        cookie.append(('Set-Cookie', value))

        self.__header = _header
        self.__cookie = cookie

    def __getitem__(self, name):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            return self.__header.get(name, None)
        else:
            return [cookie[1] for cookie in self.__cookie] or None

    def __setitem__(self, name, value):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            if value is not None:
                self.__header[name] = value
            else:
                self.__header.pop(name, None)
        else:
            if value is not None:
                self.__cookie = [('Set-Cookie', value)]
            else:
                self.__cookie = []

    def __delitem__(self, name):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            self.__header.pop(name, None)
        else:
            self.__cookie = []

    def __contains__(self, name):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            return name in self.__header
        else:
            return self.__cookie != []

    def setdefault(self, name, default_value):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            if default_value is not None:
                return self.__header.setdefault(name, default_value)
            else:
                return self.__header.get(name, None)
        else:
            if self.__cookie != []:
                return [cookie[1] for cookie in self.__cookie]
            elif default_value is not None:
                self.__cookie = [('Set-Cookie', default_value)]
                return [default_value]
            else:
                return None

    def pop(self, name, default_value=None):

        name = self._valid_name(name)
        if name != 'Set-Cookie':
            return self.__header.pop(name, default_value)
        else:
            if self.__cookie != []:
                cookie = [cookie[1] for cookie in self.__cookie]
                self.__cookie = []
                return cookie
            else:
                return None

    def add_cookie(self, name, value, expires=None, path=None, domain=None, secure=False, httponly=False):

        cookie = ['%s=%s' % (name, value)]
        if expires is not None:
            if isinstance(expires, int):
                cookie.append((datetime.utcnow() + timedelta(seconds=expires)).strftime('expires=%a, %d-%b-%Y %H:%M:%S GMT'))
            elif isinstance(expires, datetime):
                cookie.append(expires.strftime('expires=%a, %d-%b-%Y %H:%M:%S GMT'))
            else:
                cookie.append('expires=' + expires)

        if path:
            cookie.append('path=' + path)

        if domain:
            cookie.append('domain=' + domain)

        if secure:
            cookie.append('secure')

        if httponly:
            cookie.append('HttpOnly')

        self.__cookie.append(('Set-Cookie', '; '.join(cookie)))

    def get_cookies(self):

        return self.__cookie[:]

    def clear_cookies(self):

        self.__cookie = []

    def items(self):

        return self.__header.items() + self.__cookie

    def clear(self):

        self.__header = {}
        self.__cookie = []

    def __len__(self):

        return len(self.__header) + len(self.__cookie)

    @staticmethod
    def _valid_name(name):

        name = name.title()
        if name == 'Etag':
            return 'ETag'
        if name == 'X-Xss-Protection':
            return 'X-XSS-Protection'
        if name == 'Www-Authenticate':
            return 'WWW-Authenticate'
        if name == 'Content-Md5':
            return 'Content-MD5'
        return name

class Response(object):

    def __init__(self, start_response):

        self._start_response = start_response
        # set default HTTP status to 200 OK
        # 将默认的HTTP状态码设为200 OK
        self.status = 200
        self.header = ResponseHeader()
        # the string buffer for output content
        # 存储输出内容的字符串缓冲区
        self.out = StringIO.StringIO()

    def set_content_type(self, mime_type='text/html', charset='UTF-8'):

        if mime_type != 'text/html':
            if mime_type == 'xhtml':
                mime_type = self.handler.request.first_match(('application/xhtml+xml',), 'text/html')
            elif mime_type == 'wap':
                mime_type = 'text/vnd.wap.wml'
            elif mime_type == 'wap2':
                mime_type = self.handler.request.first_match(('application/vnd.wap.xhtml+xml', 'application/xhtml+xml'), 'text/html')
            elif mime_type == 'json':
                mime_type = 'application/json'
            elif mime_type == 'atom':
                mime_type = 'application/atom+xml'
                charset = ''
            elif mime_type == 'rss':
                mime_type = 'application/rss+xml'
                charset = ''

        self.header['Content-Type'] = '%s; charset=%s' % (mime_type, charset) if charset else mime_type

    def set_cache(self, seconds, is_privacy=None):
        if seconds <= 0:
            self.header['Cache-Control'] = self.header['Pragma'] = 'no-cache'
            # fix localhost test for IE 6
            # for performance reason, you can remove next line in production server
            # 在本地开发服务器上用IE 6测试会出现bug
            # 如果是在生产服务器上使用的话，可以去掉下面这行代码，减小header的体积
            # 详情可见：http://www.keakon.cn/bbs/thread-1976-1-1.html
            self.header['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
        else:
            if is_privacy:
                privacy = 'public, '
            elif is_privacy is None:
                privacy = ''
            else:
                privacy = 'private, '
            self.header['Cache-Control'] = '%smax-age=%s' % (privacy, seconds)

    def write(self, obj, encoding='utf-8'):

        if isinstance(obj, str):
            self.out.write(obj)
        elif isinstance(obj, unicode):
            self.out.write(obj.encode(encoding))
        else:
            self.out.write(str(obj))

    def get_status(self):

        return '%d %s' % (self.status, HTTP_STATUS[self.status])

    def clear(self):

        self.out.seek(0)
        self.out.truncate(0)

    def send(self):

        write = self._start_response(self.get_status(), self.header.items())

        body = self.out.getvalue()
        if body:
            write(body)


class RequestHandler(object):

    def __init__(self, request, response, default_status=405):

        self.request = request
        self.response = response
        self.__default_status = default_status
        self.update_shortcut()

    def update_shortcut(self):

        request = self.request
        response = self.response

        response.handler = self

        self.header = response.header
        self.write = response.write
        self.clear = response.clear
        self.set_content_type = response.set_content_type
        self.set_cache = response.set_cache

        self.GET = request.GET
        self.POST = request.POST
        self.HEADER = request.headers

    def get(self, *args, **kw):

        self.not_allowed()

    def head(self, *args, **kw):

        self.get(*args, **kw)

    post = options = put = delete = trace = get

    def before(self, *args, **kw):
        pass

    def after(self, *args, **kw):
        pass

    def set_status(self, code):
        
        self.response.status = code

    def error(self, code):

        self.set_status(code)
        self.clear()

    def redirect(self, url, status=302):

        # if status not in (301, 302, 303, 307) or (status in (303, 307) and self.request.environ['SERVER_PROTOCOL'] == 'HTTP/1.0'):
            # status = 302
        #TODO 需强化
        self.set_status(status)
        self.header['Location'] = urljoin(self.request.url, url)
        self.clear()

    def not_allowed(self):

        status = self.__default_status
        self.error(status)
        if status == 405:
            allow = [method.upper() for method in ('get', 'post', 'head', 'options', 'put', 'delete', 'trace')
                 # has been overriden, so must has been implemented
                 # 已被覆盖，所以必然已被实现
                if getattr(self.__class__, method) != getattr(RequestHandler, method)]
            self.header['Allow'] = ', '.join(allow)

    def handle_exception(self, exception):

        logging.error(format_exc())
        self.error(500)
        raise


class HtmlRequestHandler(RequestHandler):

    def before(self, *args, **kw):
        self.response.set_content_type()

class WSGIApplication(object):

    def __init__(self, url_mapping, default_response_class=Response, quote_path=True):

        self.quote_path = quote_path
        url_mapping_keys = []
        url_mappings = {}

        for handler_tuple in url_mapping:
            regexp = handler_tuple[0]
            handler = handler_tuple[1]
            if not regexp or not handler:
                continue

            response_class = handler_tuple[2] if len(handler_tuple) > 2 else default_response_class

            if regexp[0] != '^':
                regexp = '^' + regexp
            if regexp[-1] != '$':
                regexp += '$'
            compiled = re.compile(regexp)

            url_mappings[compiled] = (handler, response_class)
            url_mapping_keys.append(compiled)

        self.__url_mapping_keys = url_mapping_keys
        self.__url_mappings = url_mappings

    def __call__(self, environ, start_response):

        request = Request(environ)
        request_path = request.path if self.quote_path else request.path_info
        groups = ()
        groupdict = {}

        for regexp in self.__url_mapping_keys:
            handler, response_class = self.__url_mappings[regexp]
            match = regexp.match(request_path)
            if match:
                response = response_class(start_response)

                if not callable(handler):
                    # delay binding for url_path and handler_class string
                    # 推迟绑定URL路径和处理类字符串
                    try:
                        mod_name, class_name = handler.rsplit('.', 1)
                        mod = __import__(mod_name)
                        handler = getattr(mod, class_name)
                        self.__url_mappings[regexp] = handler, response_class
                    except Exception, e:
                        logging.error('Please check your URL mapping, you probably point this path "%s" to an undefined handler "%s". \n%s',
                        request_path, handler, format_exc())

                        response, handler = self.handle_not_found(request, start_response)
                        # make future requests not to match other handler
                        # 不删除它，以免后续的访问可能匹配其他的handler
                        self.__url_mappings[regexp] = handler, response.__class__
                        break
                handler = handler(request, response)
                groupdict = match.groupdict()
                if not groupdict:
                    groups = match.groups()
                break
        else:
            response, handler = self.handle_not_found(request, start_response)

        try:
            handler.before(*groups, **groupdict)
            method = request.method

            if method == 'GET':
                handler.get(*groups, **groupdict)
            elif method == 'POST':
                handler.post(*groups, **groupdict)
            elif method == "HEAD":
                handler.head(*groups, **groupdict)
            elif method == "OPTIONS":
                handler.options(*groups, **groupdict)
            elif method == "PUT":
                handler.put(*groups, **groupdict)
            elif method == "DELETE":
                handler.delete(*groups, **groupdict)
            elif method == "TRACE":
                handler.trace(*groups, **groupdict)
            else:
                # only speed up for GET & POST
                # 只为GET和POST方法提速绑定，因为getattr比较慢
                getattr(handler, method.lower())(*groups, **groupdict)
            handler.after(*groups, **groupdict)
        except Exception, e:
            handler.handle_exception(e)

        handler.response.send()
        return []

    def handle_not_found(self, request, start_response):

        response = Response(start_response)
        return response, RequestHandler(request, response, 404)

    @property
    def url_mapping(self):
        return self.__url_mappings
