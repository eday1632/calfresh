#!/usr/bin/python

"""this service loads the processed data from the worker and its file factories
into the database
"""


class DataLoader(object):
    def __init__(self, tables):
        self.tables = tables

    def load(self):
        print "loaded"
        return "result"
