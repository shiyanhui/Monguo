# -*- coding: utf-8 -*-

import motor
import pymongo

from error import *

__all__ = ['Connection']

class Connection(object):
    '''Manager the connnections.'''

    DEFAULT_CONNECTION_NAME = 'default'

    _connections = []
    _default_connection = None
    _default_db = None

    @classmethod
    def connect(cls, db_name=None, connection_name=None, 
                replica_set=False, *args, **kwargs):
        '''Connect to MongoDB.

        :Parameters:
            - `db_name(optional)`: The name of database. You can set it 
               through :meth:`~Connection.switch_database`.
            - `connection_name(optional)`: It will use the default value 
               :data:`~Connection.DEFAULT_CONNECTION_NAME` if not set.
            - `replica_set(optional)`: If true it will use 
              :class:`~motor.MotorReplicaSetClient` instead of 
              :class:`~motor.MotorClient` to create a new connection. 
        '''
        if db_name is not None and not isinstance(db_name, basestring):
            raise TypeError("Argument 'db_name' should be str type.")

        if connection_name is None:
            connection_name = cls.DEFAULT_CONNECTION_NAME

        if not isinstance(connection_name, basestring):
            raise TypeError("Argument 'connection_name' should be str type.")

        client_class = (motor.MotorReplicaSetClient if replica_set else
                        motor.MotorClient)
        try:
            motor_connection = client_class(*args, **kwargs).open_sync()
            pymongo_connection = motor_connection.sync_client()
        except Exception, e:
            raise ConnectionError("Cant't connect to mongdb.")


        cls.disconnect(connection_name)
        cls._connections.insert(0, {connection_name: 
                                    (motor_connection, pymongo_connection)})

        cls._default_connection = connection_name
        cls._default_db = db_name

    @classmethod
    def disconnect(cls, connection_name=None):
        '''Disconnect the connection.

        :Parameters:
            - `connection_name(optional)`: The connection name. If not set it 
              will disconnect the current connection. 
        '''
        if connection_name is None:
            connection_name = cls._default_connection

        for index, connection in enumerate(cls._connections):
            if connection_name in connection.keys():
                for item in connection[connection_name]:
                    item.close()
                cls._connections.pop(index)
                break

        if cls._connections:
            cls._default_connection = cls._connections[0].keys()[0]
        else:            
            cls._default_connection = None

    @classmethod
    def get_connection(cls, connection_name=None, pymongo=False):
        '''Get a connection, return None if the specified connection hasn't been created.

        :Parameters:
            - `connection_name(optional)`: The connection name. If not set it 
              will return the current connection.
            - `pymongo(optional)`: If true it will return an instance of 
              :class:`~pymongo.MongoClient` or 
              :class:`~pymongo.MongoReplicaSetClient` otherwise 
              :class:`~motor.MotorClient` or 
              :class:`~motor.MotorReplicaSetClient`.
        '''
        if connection_name is None:
            connection_name = cls._default_connection

        for connection in cls._connections:
            if connection_name in connection.keys():
                return connection[connection_name][1 if pymongo else 0]                 
        return None

    @classmethod
    def get_database(cls, connection_name=None, db_name=None, pymongo=False):
        '''Get a database. If the specified connection_name hasn't been 
           created it will raise a ConnectionError.

           :Parameters:
               - `connection_name(optional)`: It will use the current 
                 connection if not set.
               - `db_name(optional)`: Return the current database if not set.
               - `pymongo(optional)`: If true it will return an instance of 
                 :class:`~pymongo.MongoDatabase` otherwise 
                 :class:`~motor.MotorDatabase`.

        '''
        connection = cls.get_connection(connection_name, pymongo)
        if connection is None:
            raise ConnectionError("'%s' hasn't been connected." %
                                  connection_name)

        if db_name is None:
            db_name = cls._default_db

        if db_name is None:
            raise ConnectionError("Please set a database first!")

        return connection[db_name]

    @classmethod
    def get_default_database_name(cls):
        '''Return the name of current database.'''

        if cls._default_db is None:  
            raise ConnectionError("Haven't set default database.")

        return cls._default_db

    @classmethod
    def get_default_connection_name(cls):
        '''Return the name of current connection.'''

        if cls._default_connection is None:
            raise ConnectionError("Haven't connected to Mongdb")

        return cls._default_connection

    @classmethod
    def get_connection_name_list(cls):
        '''Return the connections' names.'''

        return [connection.keys()[0] for connection in cls._connections]

    @classmethod
    def switch_connection(cls, connection_name):
        '''Switch to the specified connection.

        :Parameters:
            - `connection_name`: The connection you switch to.
        '''
        if not isinstance(connection_name, basestring):
            raise TypeError("Argument 'connection_name' should be str type.")
            
        if connection_name not in cls.get_connection_name_list():
            raise ConnectionError("'%s' hasn't been connected." %
                                  connection_name)

        cls._default_connection = connection_name

    @classmethod
    def switch_database(cls, db_name):
        '''Switch to the specified database.

        :Parameters:
            - `db_name`: The database you switch to.
        '''
        if not isinstance(db_name, basestring):
            raise TypeError("Argument 'db_name' should be str type.")

        cls._default_db = db_name
