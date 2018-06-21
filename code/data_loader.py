# -*- coding: utf-8 -*-
"""This service loads the processed data from the worker and its file factories
into the database

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
    """
    """
    def __init__(self, datapath):
        self.datapath = datapath

    def load(self):
        """
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
