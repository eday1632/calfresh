#!/usr/bin/python

import ConfigParser
import logging

from web_crawler import WebCrawler
from worker import Worker
from data_loader import DataLoader

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

logger = logging.getLogger('root')


if __name__ == '__main__':
    tables = {
        'tbl_cf296': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/CF296',
        'tbl_churn_data': 'http://www.cdss.ca.gov/inforesources/CalFresh-Resource-Center/Data',
        'tbl_data_dashboard': 'http://www.cdss.ca.gov/inforesources/Data-Portal/Research-and-Data/CalFresh-Data-Dashboard',
        'tbl_dfa256': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA256',
        'tbl_dfa296': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA296',
        'tbl_dfa296x': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA296x',
        #'tbl_dfa358f': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA358F',
        #'tbl_dfa358s': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA358S',
        'tbl_stat47': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/STAT-47',
    }

    for table in tables.keys():
        try:
            crawler = WebCrawler(table, tables[table])
            result = crawler.crawl()
            if result:
                worker = Worker(result)
                processed_tables = worker.work()

                loader = DataLoader(processed_tables)
                result = loader.load()
        except Exception as ex:
            logger.exception(ex)

    crawler.clean_up()

