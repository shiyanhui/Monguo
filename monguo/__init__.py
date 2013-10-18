# -*- coding: utf-8 -*-

'''Monguo, an asynchronous MongoDB ORM for Tornado'''

VERSION = (0, 1)

def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    
    return '.'.join(map(str, VERSION))

__version__ = get_version()
