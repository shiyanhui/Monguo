# -*- coding: utf-8 -*-

import motor

class Connection(object):
	'''Connection to MongoDB.'''

	def __init__(self, async=False, *args, **kwargs):
		pass

client = motor.MotorClient().open_sync()
db = client.test
collection = db.test
