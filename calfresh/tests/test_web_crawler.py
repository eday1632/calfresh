
import unittest

from bs4 import BeautifulSoup

from web_crawler import WebCrawler, PageParser


class TestWebCrawler(unittest.TestCase):

    def setUp(self):
        self.crawler = WebCrawler(
            table='tbl_dfa256',
            url=None,
        )

    def test_crawl(self):
        pass

    def test_get_new_page(self):
        pass

    def test_get_old_page(self):
        pass

    def test_download_new_files(self):
        pass

    def test_get_filename(self):
        pass

    def testClean_up(self):
        pass


class TestPageParser(unittest.TestCase):

    def setUp(self):
        self.parser = PageParser(
            table='tbl_dfa256',
            new_page='/etc/calfresh/calfresh/tests/test_today_page.html',
            old_page='/etc/calfresh/calfresh/tests/test_yesterday_page.html',
        )

    def test_parse(self):
        self.assertIsNone(self.parser.new_soup)
        self.assertIsNone(self.parser.old_soup)
        self.assertEqual(len(self.parser.updated_paths), 0)

        self.parser.parse()

        bs = BeautifulSoup()
        self.assertEqual(type(self.parser.new_soup), type(bs))
        self.assertEqual(type(self.parser.old_soup), type(bs))
        self.assertEqual(len(self.parser.updated_paths), 1)
        self.assertIn(
            'NEW/Portals/9/DSSDB/DataTables/DFA256FY17-18.xlsx',
            self.parser.updated_paths,
        )
        self.assertNotIn(
            'OLD/Portals/9/DSSDB/DataTables/DFA256FY16-17.xlsx',
            self.parser.updated_paths,
        )

    def test_load_page_content(self):
        self.assertIsNone(self.parser.new_soup)
        self.assertIsNone(self.parser.old_soup)

        self.parser._load_page_content()
        bs = BeautifulSoup()
        self.assertEqual(type(self.parser.new_soup), type(bs))
        self.assertEqual(type(self.parser.old_soup), type(bs))

    def test_get_all_xls_urls(self):
        good_url1 = '/9/DSSDB/DataTables/DFA256FY17-18.xlsx?ver=2018-06-08-125617-450'
        good_url2 = '/9/DSSDB/DataTables/DFA256FY14-15.xls?ver=2017-08-04-083012-853'
        bunch_of_urls = [
            '/Portals/_default/Skins/CaGov - Partner/css/cagov.core.css?cdv=392',
            'javascript:__doPostBack(&#39;dnn$dnnSEARCH$cmdSearch&#39;,&#39;&#39;)',
            'http://www.cdss.ca.gov/inforesources/2018-All-County-Letters',
            good_url1,
            good_url1,
            good_url2,
        ]

        excel_urls = self.parser._get_all_xls_urls(bunch_of_urls)
        self.assertEqual(len(excel_urls), 2)
        self.assertIn(good_url1, excel_urls)
        self.assertIn(good_url2, excel_urls)

    def test_get_new_urls(self):
        self.parser._load_page_content()

        self.assertEqual(len(self.parser.updated_paths), 0)

        self.parser._get_new_urls()
        self.assertEqual(len(self.parser.updated_paths), 1)
        self.assertIn(
            'NEW/Portals/9/DSSDB/DataTables/DFA256FY17-18.xlsx',
            self.parser.updated_paths,
        )
        self.assertNotIn(
            'OLD/Portals/9/DSSDB/DataTables/DFA256FY16-17.xlsx',
            self.parser.updated_paths,
        )
