# -*- coding: utf-8 -*-

import motor

from error import *

class Connection(object):
    DEFAULT_CONNECTION_NAME = 'default'

    _connections = {}
    _default_connection = None
    _default_db = None

    @classmethod
    def connect(cls, db_name, connection_name=None, 
                replica_set=False, *args, **kwargs):

        if not isinstance(db_name, basestring):
            raise TypeError("Argument 'db_name' should be str type.")

        if connection_name is None:
            connection_name = Connection.DEFAULT_CONNECTION_NAME

        if not isinstance(connection_name, basestring):
            raise TypeError("Argument 'connection_name' should be str type.")

        Connection.disconnect(connection_name)

        client_class = (motor.MotorReplicaSetClient if replica_set else
                        motor.MotorClient)
        try:
            connection = client_class(*args, **kwargs).open_sync()
        except Exception, e:
            raise ConnectionError("Cant't connect to mongdb.")

        Connection._connections[connection_name] = connection

        Connection._default_connection = connection_name
        Connection._default_db = db_name

    @classmethod
    def disconnect(cls, connection_name=None):
        if connection_name is None:
            connection_name = Connection._default_connection
            Connection._default_connection = None

        if connection_name in Connection._connections:
            Connection._connections[connection_name].close()
            del Connection._connections[connection_name]
            del Connection._connection_setting[connection_name]

    @classmethod
    def get_connection(cls, connection_name=None):
        if connection_name is None:
            connection_name = Connection._default_connection

        return (None if connection_name not in Connection._connections else
                Connection._connections[connection_name])

    @classmethod
    def get_database(cls, connection_name=None, db_name=None):
        connection = Connection.get_connection(connection_name)
        if connection is None:
            raise ConnectionError("Mongdb has not been connected!")

        if db_name is None:
            db_name = Connection._default_db
        if db_name is None:
            raise ConnectionError("Please set a database first!")

        return connection[db_name]

    @classmethod
    def get_default_database_name(cls):
        if Connection._default_db is None:  
            raise ConnectionError("Haven't connected to Mongdb.")

        return Connection._default_db

    @classmethod
    def switch_connection(cls, connection_name):
        if connection_name not in Connection._connections:
            return False

        Connection._default_connection = connection_name
        return True

    @classmethod
    def switch_database(cls, db_name):
        Connection._default_db = db_name
