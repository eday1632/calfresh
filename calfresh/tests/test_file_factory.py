
from dateutil import parser
import unittest

import numpy

from file_factory import CF296Factory, FileFactory, initialize


class TestFileFactories(unittest.TestCase):

    def setUp(self):
        self.table = {
            'filename': 'test_data.csv',
            'path': '/etc/calfresh/calfresh/tests/test_data.csv'
        }
        self.file_factory = CF296Factory(self.table)

    def testInitialize(self):
        valid_tables = [
            {
                'source': 'tbl_cf296',
                'filename': 'tbl_cf296',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_churn_data',
                'filename': 'tbl_churn_data',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'CFDashboard-Annual.csv',
                'filename': 'CFDashboard-Annual.csv',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'CFDashboard-Quarterly.csv',
                'filename': 'CFDashboard-Quarterly.csv',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'CFDashboard-Every_Mth.csv',
                'filename': 'CFDashboard-Every_Mth.csv',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'CFDashboard-Every_3_Mth.csv',
                'filename': 'CFDashboard-Every_3_Mth.csv',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'CFDashboard-PRI_Raw.csv',
                'filename': 'CFDashboard-PRI_Raw.csv',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_dfa256',
                'filename': 'tbl_dfa256',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_dfa296x',
                'filename': 'tbl_dfa296x',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_dfa358f',
                'filename': 'tbl_dfa358f',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_dfa358s',
                'filename': 'tbl_dfa358s',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
            {
                'source': 'tbl_stat47',
                'filename': 'tbl_stat47',
                'path': '/etc/calfresh/calfresh/tests/test_data.csv',
            },
        ]

        for table in valid_tables:
            self.assertEqual(type(initialize(table).__class__), type(FileFactory))

        invalid_table = {'source': 'unknown', 'filename': 'unknown'}
        self.assertRaises(ValueError, initialize, invalid_table)

    def testAddFullDate(self):
        self.file_factory.df['month'] = 'JAN'
        self.file_factory.df['year'] = '2018'
        self.file_factory.addFullDate()
        self.assertEqual(
            self.file_factory.df['fulldate'][0],
            parser.parse('01/01/2018')
        )

    def testAddYear(self):
        valid_years = ['19', '02', '10']
        invalid_years = ['20', '01', '2009']

        for year in valid_years:
            self.file_factory.addYear(year)
            for row in self.file_factory.df.year:
                self.assertEqual(type(row), numpy.int64)

        for year in invalid_years:
            self.assertRaises(ValueError, self.file_factory.addYear, year)

        self.assertRaises(ValueError, self.file_factory.addYear, 'blah')

    def testAddMonth(self):
        self.file_factory.addMonth('jan')
        self.assertEqual(self.file_factory.df['month'][0], 'JAN')

    def testAddQuarter(self):
        self.file_factory.df['month'] = 'JUNK'
        self.file_factory.addQuarter()
        numpy.testing.assert_equal(self.file_factory.df['quarter'][0], numpy.nan)

        self.file_factory.df['month'] = 'JAN'
        self.file_factory.addQuarter()
        self.assertEqual(self.file_factory.df['quarter'][0], 1.0)

    def testCheckNumbers(self):
        pass

    def test_getValidNumber(self):
        valid_numbers = [1, 0.234, -1.123, '100', '1a2b3c']
        invalid_numbers = ['all letters', None]

        for number in valid_numbers:
            self.assertEqual(type(self.file_factory._getValidNumber(number)), float)

        for number in invalid_numbers:
            numpy.testing.assert_equal(
                self.file_factory._getValidNumber(number),
                numpy.nan,
            )

    def test_convertToNumber(self):
        pass

    def testCheckPercents(self):
        pass

    def testCheckCounties(self):
        pass

    def test_trimNonCountyRows(self):
        pass

    def test_cleanCountyNames(self):
        pass

    def test_getNearestSpelledCounties(self):
        pass

    def test_getClosestSpelledCounty(self):
        pass

    def testTrimBogusColumns(self):
        df_width = self.file_factory.df.shape[1]
        self.file_factory.trimBogusColumns()
        trimmed_width = self.file_factory.df.shape[1]

        self.assertEqual(trimmed_width, df_width - 2)

    def testTrimBogusRows(self):
        df_height = self.file_factory.df.shape[0]
        self.file_factory.trimBogusRows()
        trimmed_height = self.file_factory.df.shape[0]

        self.assertEqual(trimmed_height, df_height - 1)
