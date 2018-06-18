#!/usr/bin/python

import os
import datetime
import logging.config
import ConfigParser

import requests
from bs4 import BeautifulSoup


config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

temp_dir = config.get('filepaths', 'temp')
data_dir = config.get('filepaths', 'data')

logging.config.fileConfig(config.get('filepaths', 'config'))
logger = logging.getLogger('web_crawler')


class WebCrawler(object):
    """docstring for WebCrawler"""
    def __init__(self, table, url):
        super(WebCrawler, self).__init__()
        self.table = table
        self.url = url

    def crawl(self):
        new_page = self._get_new_page()
        old_page = self._get_old_page()

        # if we successfully received today's page
        if new_page:
            parsed_pages = PageParser(self.table, new_page, old_page)

            if parsed_pages.are_different:
                self._download_new_files(parsed_pages.updated_paths)
                return self.table

    def _get_new_page(self):
        # request page
        page = requests.get(self.url)

        if page.status_code != 200:
            logger.error('Requested page not received! \
                Page: {}, Status code: {}'.format(self.url, page.status_code))
            return None
        else:
            # save new page to file
            fp = os.path.join(temp_dir, self.table + '_' + str(datetime.date.today()))
            with open(fp, 'w') as f:
                f.write(page.text.encode('ascii', 'ignore'))

            return fp

    def _get_old_page(self):
        # return yesterday's file pointer
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return os.path.join(temp_dir, self.table + '_' + str(yesterday))

    def _download_new_files(self, updated_paths):
        # for updated link in new page, download the file
        for path in updated_paths:
            if 'http' not in path:
                path = 'http://www.cdss.ca.gov' + path

            filename = self._get_filename(path)
            fp = os.path.join(data_dir, self.table, 'xlsx', filename)

            response = requests.get(path)
            with open(fp, 'wb') as output:
                output.write(response.content)
                logger.info('Downloaded %s', fp)

    def _get_filename(self, path):
        filename = path.split('/')[-1]
        if '?ver' in path:
            filename = filename.split('?')[0]

        return filename

    def _process_new_files(self):
        # dispatch the worker to process the new files!
        pass

    def clean_up(self):
        two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(str(two_days_ago)):
                    os.remove(os.path.join(temp_dir, file))


class PageParser(object):
    """docstring for PageParser"""
    def __init__(self, table, new_page, old_page):
        super(PageParser, self).__init__()
        self.table = table
        self.new_page = new_page
        self.old_page = old_page
        self.new_soup = None
        self.old_soup = None
        self.updated_paths = []

        self._extract_page_content()
        self._get_new_versions()

    @property
    def are_different(self):
        return len(self.updated_paths) > 0

    def _extract_page_content(self):
        # open new page from file
        with open(self.new_page, 'r') as new:
            self.new_soup = BeautifulSoup(new.read(), 'html.parser')
        # open old page from file
        with open(self.old_page, 'r') as old:
            self.old_soup = BeautifulSoup(old.read(), 'html.parser')

    def _get_xls_links(self, link_list):
        file_set = set()
        for link in link_list:
            if '.xls' in link:
                file_set.add(link)
        return file_set

    def _get_new_versions(self):
        all_new_links = [str(link.get('href')) for link in self.new_soup.find_all('a')]
        all_old_links = [str(link.get('href')) for link in self.old_soup.find_all('a')]

        new_file_set = self._get_xls_links(all_new_links)
        old_file_set = self._get_xls_links(all_old_links)

        for link in new_file_set:
            if link not in old_file_set:
                self.updated_paths.append(link)
                logger.info('Found a new link! %s', link)
















