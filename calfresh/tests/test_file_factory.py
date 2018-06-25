
import unittest

from file_factory import FileFactory, initialize


class TestFileFactories(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testInitialize(self):
        valid_tables = [
            {
                'source': 'tbl_cf296',
                'filename': 'tbl_cf296',
            },
            {
                'source': 'tbl_churn_data',
                'filename': 'tbl_churn_data',
            },
            {
                'source': 'CFDashboard-Annual.csv',
                'filename': 'CFDashboard-Annual.csv',
            },
            {
                'source': 'CFDashboard-Quarterly.csv',
                'filename': 'CFDashboard-Quarterly.csv',
            },
            {
                'source': 'CFDashboard-Every_Mth.csv',
                'filename': 'CFDashboard-Every_Mth.csv',
            },
            {
                'source': 'CFDashboard-Every_3_Mth.csv',
                'filename': 'CFDashboard-Every_3_Mth.csv',
            },
            {
                'source': 'CFDashboard-PRI_Raw.csv',
                'filename': 'CFDashboard-PRI_Raw.csv',
            },
            {
                'source': 'tbl_dfa256',
                'filename': 'tbl_dfa256',
            },
            {
                'source': 'tbl_dfa296x',
                'filename': 'tbl_dfa296x',
            },
            {
                'source': 'tbl_dfa358f',
                'filename': 'tbl_dfa358f',
            },
            {
                'source': 'tbl_dfa358s',
                'filename': 'tbl_dfa358s',
            },
            {
                'source': 'tbl_stat47',
                'filename': 'tbl_stat47',
            },
        ]

        for table in valid_tables:
            self.assertEqual(type(initialize(table).__class__), type(FileFactory))

        invalid_table = {'source': 'unknown', 'filename': 'unknown'}
        self.assertRaises(ValueError, initialize, invalid_table)

    def testAddFullDate(self):
        pass

    def testAddYear(self):
        pass

    def testAddMonth(self):
        pass

    def testAddQuarter(self):
        pass

    def testCheckNumbers(self):
        pass

    def test_getValidNumber(self):
        pass

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
        pass

    def testTrimBogusRows(self):
        pass
