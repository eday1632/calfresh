# -*- coding: utf-8 -*-
"""Loads the processed data from the worker and its factories into the database

Attributes:
    Just your standard config and logging stuff

"""

from os import walk
from os.path import join
import ConfigParser
import csv
import logging.config
import subprocess

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

logging.config.fileConfig(config.get('filepaths', 'config'))
logger = logging.getLogger('data_loader')


class DataLoader(object):
    """Load the data into the database!

    This simple class takes a datapath to the latest processed files and then
    loads these into their respective tables in the database

    Args:
        datapath (str): formatted as '/etc/calfresh/MM_DD_YYYY'

    """
    def __init__(self, datapath):
        self.datapath = datapath

    def load(self):
        """Load the data in the date-named directory using a subprocess

        Here we extract the filenames from the directory, get the headers for each,
        and then load them into the MySQL database with a system command through
        python's subprocess module

        """
        with open('/etc/calfresh/logs/calfresh.log', 'a') as logfile:
            for root, dirs, files in walk(self.datapath):
                for table_name in files:
                    logger.info('Loading %s', table_name)
                    with open(join(self.datapath, table_name)) as csvfile:
                        header = csv.reader(csvfile, delimiter=',').next()
                        try:
                            result = subprocess.call([
                                'mysqlimport',
                                '--local',
                                '--replace',
                                '--fields-terminated-by=,',
                                '--ignore-lines=1',
                                '--columns=' + ','.join(header),
                                '-u',
                                'eday',
                                'calfreshdb',
                                join(self.datapath, table_name),
                            ], stdout=logfile)
                            logger.info('Load result: %s', result)
                        except Exception as ex:
                            logger.exception(ex)
