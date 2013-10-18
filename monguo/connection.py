# -*- coding: utf-8 -*-

import motor
import pymongo

from error import *

class Connection(object):
    DEFAULT_CONNECTION_NAME = 'default'

    _connections = {}
    _default_connection = None
    _default_db = None

    @classmethod
    def connect(cls, db_name=None, connection_name=None, 
                replica_set=False, *args, **kwargs):

        if db_name is not None and not isinstance(db_name, basestring):
            raise TypeError("Argument 'db_name' should be str type.")

        if connection_name is None:
            connection_name = cls.DEFAULT_CONNECTION_NAME

        if not isinstance(connection_name, basestring):
            raise TypeError("Argument 'connection_name' should be str type.")

        cls.disconnect(connection_name)

        client_class = (motor.MotorReplicaSetClient if replica_set else
                        motor.MotorClient)
        try:
            motor_connection = client_class(*args, **kwargs).open_sync()
            pymongo_connection = motor_connection.sync_client()
        except Exception, e:
            raise ConnectionError("Cant't connect to mongdb.")

        cls._connections[connection_name] = (motor_connection,
                                             pymongo_connection)

        cls._default_connection = connection_name
        cls._default_db = db_name

    @classmethod
    def disconnect(cls, connection_name=None):
        if connection_name is None:
            connection_name = cls._default_connection
            cls._default_connection = None

        if connection_name in cls._connections:
            for connection in cls._connections[connection_name]:
                connection.close()
            del cls._connections[connection_name]

    @classmethod
    def get_connection(cls, connection_name=None, pymongo=False):
        if connection_name is None:
            connection_name = cls._default_connection

        if connection_name not in cls._connections:
            return None

        if pymongo:
            return cls._connections[connection_name][1]

        return cls._connections[connection_name][0]

    @classmethod
    def get_database(cls, connection_name=None, db_name=None, pymongo=False):
        connection = cls.get_connection(connection_name, pymongo)
        if connection is None:
            raise ConnectionError("Mongdb has not been connected!")

        if db_name is None:
            db_name = cls._default_db

        if db_name is None:
            raise ConnectionError("Please set a database first!")

        return connection[db_name]

    @classmethod
    def get_default_database_name(cls):
        if cls._default_db is None:  
            raise ConnectionError("Haven't connected to Mongdb.")

        return cls._default_db

    @classmethod
    def switch_connection(cls, connection_name):
        if not isinstance(connection_name, basestring):
            raise TypeError("Argument 'connection_name' should be str type.")
            
        if connection_name not in cls._connections:
            return False

        cls._default_connection = connection_name
        return True

    @classmethod
    def switch_database(cls, db_name):
        if not isinstance(db_name, basestring):
            raise TypeError("Argument 'db_name' should be str type.")

        cls._default_db = db_name
