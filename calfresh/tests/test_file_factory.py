
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

    def test_initialize(self):
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

    def test_add_full_date(self):
        self.file_factory.df['month'] = 'JAN'
        self.file_factory.df['year'] = '2018'
        self.file_factory.add_full_date()
        self.assertEqual(
            self.file_factory.df['fulldate'][0],
            parser.parse('01/01/2018')
        )

    def test_add_year(self):
        valid_years = ['19', '02', '10']
        invalid_years = ['20', '01', '2009']

        for year in valid_years:
            self.file_factory.add_year(year)
            for row in self.file_factory.df.year:
                self.assertEqual(type(row), numpy.int64)

        for year in invalid_years:
            self.assertRaises(ValueError, self.file_factory.add_year, year)

        self.assertRaises(ValueError, self.file_factory.add_year, 'blah')

    def test_add_month(self):
        self.file_factory.add_month('jan')
        self.assertEqual(self.file_factory.df['month'][0], 'JAN')

    def test_add_quarter(self):
        self.file_factory.df['month'] = 'JUNK'
        self.file_factory.add_quarter()
        numpy.testing.assert_equal(self.file_factory.df['quarter'][0], numpy.nan)

        self.file_factory.df['month'] = 'JAN'
        self.file_factory.add_quarter()
        self.assertEqual(self.file_factory.df['quarter'][0], 1.0)

    def test_check_numbers(self):
        pass

    def test_get_valid_number(self):
        valid_numbers = [1, 0.234, -1.123, '100', '1a2b3c']
        invalid_numbers = ['all letters', None]

        for number in valid_numbers:
            self.assertEqual(type(self.file_factory._get_valid_number(number)), float)

        for number in invalid_numbers:
            numpy.testing.assert_equal(
                self.file_factory._get_valid_number(number),
                numpy.nan,
            )

    def test_convert_to_number(self):
        self.assertEqual(
            self.file_factory._convert_to_number('1a2b3c.4d'),
            123.4
        )

        numpy.testing.assert_equal(
            self.file_factory._convert_to_number(''),
            numpy.nan,
        )

        numpy.testing.assert_equal(
            self.file_factory._convert_to_number(None),
            numpy.nan,
        )

    def test_check_percents(self):
        pass

    def test_check_counties(self):
        pass

    def test_trim_noncounty_rows(self):
        pass

    def test_clean_county_names(self):
        pass

    def test_get_nearest_spelled_counties(self):
        too_few_letters = 'SantaCl'
        too_many_letters = 'SantaClaraWUT?'
        just_enough_letters = 'SantaClara/a'
        exact_letters = 'SSSSSSSSSS'

        too_few = self.file_factory._get_nearest_spelled_counties(too_few_letters)
        too_many = self.file_factory._get_nearest_spelled_counties(too_many_letters)
        just_enough = self.file_factory._get_nearest_spelled_counties(just_enough_letters)
        exact = self.file_factory._get_nearest_spelled_counties(exact_letters)

        self.assertNotIn('SantaClara', too_few)
        self.assertNotIn('SantaClara', too_many)
        self.assertIn('SantaClara', just_enough)
        self.assertIn('SantaClara', exact)

        self.assertEqual(just_enough['SantaClara'], 2L)
        self.assertEqual(exact['SantaClara'], 9L)

    def test_get_closest_spelled_county(self):
        pass

    def test_trim_bogus_columns(self):
        df_width = self.file_factory.df.shape[1]
        self.file_factory.trim_bogus_columns()
        trimmed_width = self.file_factory.df.shape[1]

        self.assertEqual(trimmed_width, df_width - 2)

    def test_trim_bogus_rows(self):
        df_height = self.file_factory.df.shape[0]
        self.file_factory.trim_bogus_rows()
        trimmed_height = self.file_factory.df.shape[0]

        self.assertEqual(trimmed_height, df_height - 1)
