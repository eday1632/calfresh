# -*- coding: utf-8 -*-
"""This module contains the WebCrawler and PageParser for identifying and downloading
    new and updated CalFresh excel files

Attributes:
    config (RawConfigParser): for reading the configuration file
    temp_dir (str): the temporary directory to use for saving html files
    data_dir (str): the directory containing all the excel and csv files
    logger (Logger): the object for logging

"""

import ConfigParser
import datetime
import logging.config
import os

from bs4 import BeautifulSoup
import requests

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

temp_dir = config.get('filepaths', 'temp')
data_dir = config.get('filepaths', 'data')

logging.config.fileConfig(config.get('filepaths', 'config'))
logger = logging.getLogger('web_crawler')


class WebCrawler(object):
    """The WebCrawler gets today's and yesterday's html files for a given url
        and uses the PageParser to identify new and updated files

    Args:
        table (str): the table we're currently working on
        url (str): the url for the table's data

    Returns:
        table (str): the table for the next process (Worker) to consume

    """
    def __init__(self, table, url):
        super(WebCrawler, self).__init__()
        self.table = table
        self.url = url

    def crawl(self):
        """Do the needful: get all the html pages, identify new urls, and return them"""
        new_page = self._get_new_page()
        old_page = self._get_old_page()

        # if we successfully received today's page
        if new_page:
            parser = PageParser(self.table, new_page, old_page)
            parser.parse()

            if len(self.updated_paths) > 0:  # if there's new urls
                self._download_new_files(parser.updated_paths)
                return self.table

    def _get_new_page(self):
        """Get the html page as it exists today"""
        page = requests.request('GET', self.url)

        if page.status_code != 200:
            logger.error('Requested page not received! Page: {}, Status code: {}'.format(
                self.url,
                page.status_code,
            ))
        else:
            filepath = os.path.join(
                temp_dir,
                self.table + '_' + str(datetime.date.today()),
            )
            with open(filepath, 'w') as f:
                f.write(page.text.encode('ascii', 'ignore'))

            return filepath

    def _get_old_page(self):
        """Return the string path of yesterday's file"""
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return os.path.join(temp_dir, self.table + '_' + str(yesterday))

    def _download_new_files(self, updated_paths):
        """For updated link in new page, download the file

        Args:
            updated_paths (list of str): the urls containing new or updated files

        Outputs:
            Excel files in their corresponding table's directory

        """
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
        """Get the file name from the url

        Args:
            path (str): the url path containing the file name at the end

        Returns:
            filename (str): the name of the excel file

        """
        filename = path.split('/')[-1]
        if '?ver' in path:
            filename = filename.split('?')[0]

        return filename

    def clean_up(self):
        """Remove the html files that are older than yesterday's"""
        two_days_ago = datetime.date.today() - datetime.timedelta(days=2)
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(str(two_days_ago)):
                    os.remove(os.path.join(temp_dir, file))


class PageParser(object):
    """This class looks for new Excel files by comparing today's and yesterday's pages

    Args:
        table (str): the table whose pages to get
        new_page (str): a link to the saved html
        old_page (str): another link to saved html

    Attributes:
        new_soup (BeautifulSoup obj): parsed html from today's page
        old_soup (BeautifulSoup obj): parsed html from yesterday's page
        updated_paths (list of str): all the new excel file urls

    """
    def __init__(self, table, new_page, old_page):
        super(PageParser, self).__init__()
        self.table = table
        self.new_page = new_page
        self.old_page = old_page
        self.new_soup = None
        self.old_soup = None
        self.updated_paths = []

    def parse(self):
        """Load the html into BeautifulSoup and get the new excel urls"""
        self._load_page_content()
        self._get_new_urls()

    def _load_page_content(self):
        """Extract the new and old html into beautiful soup objects"""
        with open(self.new_page, 'r') as new:
            self.new_soup = BeautifulSoup(new.read(), 'html.parser')

        with open(self.old_page, 'r') as old:
            self.old_soup = BeautifulSoup(old.read(), 'html.parser')

    def _get_all_xls_urls(self, url_list):
        """Extract the urls to excel files from all urls found

        Args:
            url_list (list of str): all the urls found on the page

        Returns:
            file_urls (set of str): all the urls to excel files

        """
        file_urls = set()
        for url in url_list:
            if '.xls' in url:
                file_urls.add(url)
        return file_urls

    def _get_new_urls(self):
        """Get any excel file urls that changed or weren't there yesterday"""
        all_new_urls = [str(url.get('href')) for url in self.new_soup.find_all('a')]
        all_old_urls = [str(url.get('href')) for url in self.old_soup.find_all('a')]

        new_xls_url_set = self._get_all_xls_urls(all_new_urls)
        old_xls_url_set = self._get_all_xls_urls(all_old_urls)

        for url in new_xls_url_set:
            if url not in old_xls_url_set:
                self.updated_paths.append(url)
                logger.info('Found a new url! %s', url)
