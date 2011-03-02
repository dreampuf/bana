#!/usr/bin/env python
# -*- coding: utf-8 -*-
# discription: admin_url 
# author: dreampuf

import sys, os 
CURPATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(CURPATH, "lib"))



def main():
    application = que.WSGIApplication([("^/$", MainHandler)])

    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
