#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2014-03-26 14:00:01
# @Last Modified by:   lime
# @Last Modified time: 2014-03-26 14:01:16

from motor import MotorClient, MotorDatabase, MotorReplicaSetClient
from tornado.testing import AsyncTestCase, gen_test
from monguo.connection import Connection
from monguo.document import Document
from monguo.field import *

class FieldTest(AsyncTestCase):
    pass
