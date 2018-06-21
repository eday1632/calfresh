# -*- coding: utf-8 -*-
"""This is the main application for controlling the three core services

The app runs the WebCrawler, Worker, and DataLoader.

Attributes:
    config (RawConfigParser): for reading the configuration file
    logger (Logger): the object for logging

"""

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
            result = crawler.crawl()

            if result:
                worker = Worker(result)
                processed_tables = worker.work()

                loader = DataLoader(processed_tables)
                result = loader.load()

        except Exception as ex:
            logger.exception(ex)

    crawler.clean_up()
    logger.info('finished')
