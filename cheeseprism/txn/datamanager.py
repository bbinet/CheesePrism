"""
transaction datamanager
"""
from . import savepoint
from path import path
import json
import os
import transaction


class JSON(object):

    transaction_manager = transaction.manager
    savepoint_factory = savepoint.DictSavepoint
    
    def __init__(self, writer):
        self.write = writer
        self.uncommitted = {}
        self.committed = self.uncommitted.copy()

    def __getitem__(self, name):
        return self.uncommitted[name]

    def __setitem__(self, name, value):
        self.uncommitted[name] = value

    def __delitem__(self, name):
        del self.uncommitted[name]

    def keys(self):
        return self.uncommitted.keys()

    def values(self):
        return self.uncommitted.values()

    def items(self):
        return self.uncommitted.items()

    def __repr__(self):
        return self.uncommitted.__repr__()

    def abort(self, transaction):
        self.uncommitted = self.committed.copy()

    def tpc_begin(self, transaction):
        pass

    def commit(self, transaction):
        pass

    def tpc_vote(self, transaction):
        devnull = open(os.devnull, 'wb')
        try:
            json.dump(self.uncommitted, devnull)
        except TypeError as e:
            raise ValueError("Unpickleable value cannot be saved: %s" %e.message)

    def tpc_finish(self, transaction):
        self.write(self.uncommitted)
        self.committed = self.uncommitted.copy()

    def tpc_abort(self, transaction):
        self.uncommitted = self.committed.copy()

    def sortKey(self):
        return 'json_dm' + str(id(self))

    def savepoint(self):
        return self.savepoint_factory(self)


class JSONFile(JSON):

    def write(self, data):
        with open(self.filepath, 'w') as stream:
            json.dump(data, stream)

    def __init__(self, filepath):
        self.filepath = path(filepath)
        self.uncommitted = {}
        if self.filepath.exists():
            with open(self.filepath) as stream:
                self.uncommitted = json.load(stream) 
        


