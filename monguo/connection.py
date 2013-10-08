# -*- coding: utf-8 -*-

import motor
from error import *

class Connection(object):
	'''Connection to MongoDB.'''

    DEFAULT_CONNECTION_NAME = 'default'

    _connection_setting = {}
    _connections        = {}
    _dbs                = {}

	def __init__(self, db_name, alias=Connection.DEFAULT_CONNECTION_NAME, replica_set=False, *args, **kwargs):
        self._alias = alias
        self._client_class = motor.MotorReplicaSetClient if replica_set else MotorClient
        self._args = args
        self._kwargs = kwargs
        self._db_name = db_name
	    
    def connect(self):
        if self._alias not in Connection._connections:
            try:
                connection = self._client_class(*self._args, **self._kwargs).open_sync()
            except Exception, e:
                raise ConnectionErroe('Cant\'t connect to mongdb.')
            Connection._connection_setting[self._alias] = {'args': args, 'kwargs': kwargs}
            Connection._connections[self.alias] = connection
            Connection._dbs[self._alias] = connection[self._db_name]
        elif not Connection._connections[self._alias].connected:
            args = Connection._connection_setting[self._alias]['args']
            kwargs = Connection._connection_setting[self._alias]['kwargs']
            try:
                connection = self._client_class(*args, **kwargs).open_sync()
            except Exception, e:
                raise ConnectionErroe('Cant\'t connect to mongdb.')

            Connection._connections[self._alias].close()
            Connection._connections[self._alias] = connection
            Connection._dbs[self._alias] = connection[self._db_name]
        return Connection._connections[self._alias]

    def disconnect(self):
        if self._alias in Connection._connections:
            if Connection._connections[self._alias].connected:
                Connection._connections[self._alias].close()
            del Connection._connections[self._alias]
            del Connection._connection_setting[self._alias]
            del Connection._dbs[self._alias]

    @classmethod
    def get_db(cls, db_name, alias=DEFAULT_CONNECTION_NAME):
        return None if alias not in Connection._dbs else Connection._dbs[alias]

