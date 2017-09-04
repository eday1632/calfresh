#!/usr/bin/python

import time, os, sys, webbrowser, tempfile, datetime

import requests
from bs4 import BeautifulSoup


temp_dir = '/etc/calfresh/temp'


class WebCrawler(object):
	"""docstring for WebCrawler"""
	def __init__(self, table, url):
		super(WebCrawler, self).__init__()
		self.table = table
		self.url = url

	def run(self):
		new_page = self._get_new_page()
		old_page = self._get_old_page()

		parsed_pages = PageParser(self.table, new_page, old_page)

		if parsed_pages.are_different:
			self._download_new_files(parsed_pages.updated_files)
			self._process_new_files()

	def _get_new_page(self):
		# request page
		page = requests.get(self.url)
		# save new page to file
		fp = os.path.join(temp_dir, self.table + '_' + str(datetime.date.today()))
		with open(fp, 'w') as f:
			f.write(page.text.encode('ascii', 'ignore'))

		return fp

	def _get_old_page(self):
		# return yesterday's file pointer
		yesterday = datetime.date.today() - datetime.timedelta(days=1)
		return os.path.join(temp_dir, self.table + '_' + str(yesterday))

	def _download_new_files(self, updated_files):
		# for updated link in new page, download the file
		for file in updated_files:
			if 'http' not in file:
				file = 'http://www.cdss.ca.gov' + file
			response = requests.get(file)
			fp = os.path.join(temp_dir, self.table + '.xls')
			with open(fp, 'w') as output:
				output.write(response.content)

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
		self.updated_files = []

		self._extract_page_content()
		self._get_new_versions()

	@property
	def are_different(self):
		return len(self.updated_files) > 0

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
				self.updated_files.append(link)


if __name__ == '__main__':
	tables = {
		'tbl_cf296': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/CF296',
		'tbl_churn_data': 'http://www.cdss.ca.gov/inforesources/CalFresh-Resource-Center/Data',
		'tbl_data_dashboard': 'http://www.cdss.ca.gov/inforesources/Data-Portal/Research-and-Data/CalFresh-Data-Dashboard',
		'tbl_dfa256': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA256',
		'tbl_dfa296': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA296',
		'tbl_dfa296x': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA296x',
		'tbl_dfa358f': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA358F',
		'tbl_dfa358s': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/DFA358S',
		'tbl_stat47': 'http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables/STAT-47',
		}

	for table in tables.keys():
		print table
		wc = WebCrawler(table, tables[table])
		wc.run()

	wc.clean_up()

















