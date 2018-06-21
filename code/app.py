
import ConfigParser
import logging

from constants import constants
from data_loader import DataLoader
from web_crawler import WebCrawler
from worker import Worker

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

logger = logging.getLogger('root')


if __name__ == '__main__':
    constants = constants()

    logger.info('starting...')
    for table in constants.table_url_map.keys():
        try:
            crawler = WebCrawler(table, constants.table_url_map[table])
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
