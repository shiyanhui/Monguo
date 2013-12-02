#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-25 19:45:09
# @Last Modified by:   lime
# @Last Modified time: 2013-12-02 22:07:21

'''Monguo, an asynchronous MongoDB ORM for Tornado'''

from connection import *
from document import *
from field import *
from error import *


VERSION = (0, 1, 5)

def get_version():
    if isinstance(VERSION[-1], basestring):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    
    return '.'.join(map(str, VERSION))

__version__ = get_version()
