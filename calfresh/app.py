# -*- coding: utf-8 -*-
"""This is the main application for controlling the three core services

The app runs the WebCrawler, Worker, and DataLoader.

Attributes:
    config (RawConfigParser): for reading the configuration file
    logger (Logger): the object for logging

"""

from os.path import join
import ConfigParser
import logging

from constants import table_url_map
from data_loader import DataLoader
from web_crawler import WebCrawler
from worker import Worker

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

logger = logging.getLogger('root')


if __name__ == '__main__':

    logger.info('starting...')
    for table in table_url_map.keys():
        try:
            crawler = WebCrawler(table, table_url_map[table])
            new_table_data = crawler.crawl()

            if new_table_data:
                worker = Worker(new_table_data)
                datapath = worker.work()

                loader = DataLoader()
                table += '.csv'
                loader.load(join(datapath, table))

        except Exception as ex:
            logger.exception(ex)

    crawler.clean_up()
    logger.info('finished')
