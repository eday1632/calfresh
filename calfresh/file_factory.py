# -*- coding: utf-8 -*-
"""FileFactory module containing base and subclasses
TODOs:
    Finish documentation
    Build tests
    Possibly refactor for better testing

"""

from abc import ABCMeta, abstractmethod
from string import digits
import ConfigParser
import logging.config

from xlrd.xldate import xldate_as_datetime
import editdistance
import numpy as np
import pandas as pd

import constants

config = ConfigParser.RawConfigParser()
config.read('/etc/calfresh/calfresh.conf')

logging.config.fileConfig(config.get('filepaths', 'config'))
logger = logging.getLogger('file_factory')


def initialize(item):
    """Initializes the proper FileFactory object based on the source directory
    of the item

    Args:
        item (dict): object with path, source and filename keys

    Returns:
        FileFactory: subclass corresponding to the source of the item

    Raises:
        ValueError: If the source of the item is unrecognized

    """
    if item['source'] == 'tbl_cf296':
        return CF296Factory()
    if item['source'] == 'tbl_churn_data':
        return ChurnDataFactory()
    if item['filename'] == 'CFDashboard-Annual.csv':
        return DataDashboardAnnualFactory()
    if item['filename'] == 'CFDashboard-Quarterly.csv':
        return DataDashboardQuarterlyFactory()
    if item['filename'] == 'CFDashboard-Every_Mth.csv':
        return DataDashboardMonthlyFactory()
    if item['filename'] == 'CFDashboard-Every_3_Mth.csv':
        return DataDashboard3MthFactory()
    if item['filename'] == 'CFDashboard-PRI_Raw.csv':
        return DataDashboardPRIRawFactory()
    if item['source'] == 'tbl_dfa256':
        return DFA256Factory()
    if item['source'] == 'tbl_dfa296x':
        return DFA296XFactory()
    if item['source'] == 'tbl_dfa358f':
        return DFA358FFactory()
    if item['source'] == 'tbl_dfa358s':
        return DFA358SFactory()
    if item['source'] == 'tbl_stat47':
        return Stat47Factory()

    raise ValueError


class FileFactory(object):
    """Base class for all the file factories

    Attributes:
        df (pandas DataFrame): the csv file passed in converted to a \
        pd.DataFrame object
        filename (str): name of the csv file
        constants (obj constants): an object with lists of column names to \
         label the factories' df attributes and a dict of county \
         keys and values
        year (int): the year (yyyy) pertaining to the data within the factory
        quarter (int) the quarter pertaining to the data within the factory
        month (str): the month (MMM) pertaining to the data within the factory

    """
    __metaclass__ = ABCMeta

    def __str__(self):
        """Returns the first ten rows of the df attribute"""
        return str(self.df.head(10))

    def build(self):
        self.trimBogusRows()
        self.trimBogusColumns()

        self.checkCounties()

        self.buildSpecific()

        self.df = self.df.fillna(value='\N')

        self.addQuarter()
        self.addFullDate()

    @abstractmethod
    def buildSpecific(self):
        """Process class specific info, such as column names, year, month, etc."""
        return

    def addFullDate(self):
        """Convert the month and year to valid datetime"""
        self.df['fulldate'] = self.df.month + '/' + self.df.year.map(str)
        self.df.fulldate = pd.to_datetime(self.df.fulldate)

    def addYear(self, year):
        """Add the year to the df and set the year attribute

        Args:
            year (str): is passed in as a slice of the filename

        Sets:
            df['year'] (pandas Series): creates the year column
             and sets its value
            year (int): converts the year argument to a number

        Raises:
            ValueError: If the year is earlier than 2002 or later than 2018

        """
        if int('20' + year) > 2019 or int('20' + year) < 2002:
            logging.error('Bad year value: %s', year)
            raise ValueError

        self.df['year'] = int('20' + year)

    def addMonth(self, month):
        """Month is passed in as a string or slice of the filename"""
        self.df['month'] = month.upper()

    def addQuarter(self):
        """Map the month to the quarter"""
        quarters = {
            'JAN': 1.0,
            'FEB': 1.0,
            'MAR': 1.0,
            'APR': 2.0,
            'MAY': 2.0,
            'JUN': 2.0,
            'JUL': 3.0,
            'AUG': 3.0,
            'SEP': 3.0,
            'OCT': 4.0,
            'NOV': 4.0,
            'DEC': 4.0,
        }

        self.df['quarter'] = self.df.month.map(quarters)

    def checkNumbers(self, startCol=1):
        """Check the type of all values in the input columns

        Args:
            startCol (int): the first column to start looking for, enforcing numerics

        Outputs:
            A squeaky clean set of columns filled with numeric or None values

        """
        for col in self.df.columns[startCol:]:
            i = 0
            for row in self.df[col]:
                self.df.loc[i, col] = self._getValidNumber(row)
                i += 1

    def _getValidNumber(self, num):
        """Extract a number from the input arg or return None

        Args:
            num (int): a value from a cell assumed to be a numeric

        Returns:
            float or None: float if there were numeric values in the arg,
            or None if it was just junk

        """
        try:
            return float(num)
        except ValueError:
            return self._convertToNumber(num)

    def _convertToNumber(self, num):
        """Remove all non-numeric characters from the input

        Args:
            num (str): a string representation of a number

        Returns:
            float stripped of all non-numerics or None

        """
        temp = num
        for c in temp:
            if c not in digits + '.':
                num = num.replace(c, '')

        try:
            return float(num)
        except ValueError:
            return np.nan

    def checkPercents(self, cols):
        """Check and standardize all percentages to fall between -1.00 and 1.00

        Args:
            cols (list of str): columns that should contain percent values

        """
        for col in cols:
            if col in self.df.columns:
                i = 0
                for row in self.df[col]:
                    if row > 1.0 or row < -1.0:
                        self.df.loc[i, col] = row / 100.0
                    i += 1

    def checkCounties(self, col=0):
        """Make sure all counties are present

        This function checks that all counties are there and if any are misspelled
        it tries to identify which county it might be

        Args:
            col (int): the column to scan for county names

        Raises:
            ValueError if after its best effort a county is still missing

        """
        # get the column name
        col = self.df.columns[col]

        self._cleanCountyNames(col)

        self.df[col] = self.df[col].replace({'Statewide': 'California'})

        self._trimNonCountyRows(col)
        constants.county_set.discard('Statewide')  # since we just changed it to Cali'
        # make sure all the counties are present
        observed = set(self.df[col].values)
        if not observed == constants.county_set:
            logging.error('Observed: %s', str(observed))
            logging.error(
                'Counties not found: %s',
                str(constants.county_set.difference(observed))
            )
            raise ValueError

    def _trimNonCountyRows(self, col):
        """Remove any blank row from the county column"""
        self.df = self.df.dropna(subset=[col]).reset_index(drop=True)

    def _cleanCountyNames(self, col):
        """Fill each cell with a valid county name or None

        Args:
            col (str): the column with observable county names

        """
        self.df[col] = self.df[col].str.strip()
        i = 0
        for county in self.df[col]:
            if county not in constants.county_set:
                if type(county) == str:
                    county = county.replace(' ', '')
                    closest = self._getClosestSpelledCounty(county)
                    self.df.loc[i, col] = closest
                else:
                    self.df.loc[i, col] = np.nan
            i += 1

    def _getNearestSpelledCounties(self, county):
        """Get county names with the shortest edit distance to the county arg

        Args:
            county (str): the invalid county name

        Returns:
            A dict of county names whose edit distance is less than 3 from the arg

        """
        vals = {}
        for key in constants.county_dict.keys():
            county = str(county)
            # Less than three is best since some counties only have four letters
            if len(county) < (len(key) + 3) and len(county) > (len(key) - 3):
                vals[key] = editdistance.eval(key, county)

        return vals

    def _getClosestSpelledCounty(self, county):
        """Get the county with the smallest edit distance or None

        Args:
            county (str): invalid county name to replace

        Returns:
            A valid county name or None if there were none within 3 edits

        """
        potentials = self._getNearestSpelledCounties(county)
        if not potentials:
            return np.nan

        closest = min(potentials, key=potentials.get)
        # Needs to have fewer than three edits made
        if potentials[closest] < 3L:
            return constants.county_dict[closest]
        else:
            return np.nan

    def trimBogusColumns(self):
        """Drop columns off the end of the table with more than a quarter empty rows"""
        rowcount = self.df.shape[0] / 4
        while self.df[self.df.columns[-1]].isnull().sum() > rowcount:
            self.df.drop(self.df.columns[-1], axis=1, inplace=True)

    def trimBogusRows(self):
        """Drop rows off the bottom of the table with more than half empty columns"""
        colcount = self.df.shape[1] / 2
        while self.df.iloc[-1].isnull().sum() > colcount:
            self.df.drop(self.df.index[-1], inplace=True)


class CF296Factory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        # drop columns with data we don't need
        self.df.drop(
            [
                self.df.columns[0],
                self.df.columns[2],
                self.df.columns[3],
                self.df.columns[4],
                self.df.columns[5],
            ],
            axis=1,
            inplace=True,
        )
        super(CF296Factory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        # dates in this column come in excel number format
        date_info = [
            xldate_as_datetime(xldate, 0) for xldate in self.df[self.df.columns[1]]
        ]

        self.df['year'] = [pydate.strftime('%Y').upper() for pydate in date_info]
        self.df['month'] = [pydate.strftime('%b').upper() for pydate in date_info]

        self.df.drop(self.df.columns[1], axis=1, inplace=True)
        self.df.columns = constants.CF296Columns


class ChurnDataFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(ChurnDataFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        if self.filename[0] in digits:
            self.addYear(self.filename[2:4])
        else:
            self.addYear(self.filename[4:6])

        Q1 = ['Q1', 'JAN']
        Q2 = ['Q2', 'APRIL']
        Q3 = ['Q3', 'JUL']
        Q4 = ['Q4', 'OCT']

        if any(indicator in self.filename for indicator in Q1):
            self.addMonth('MAR')
        elif any(indicator in self.filename for indicator in Q2):
            self.addMonth('JUN')
        elif any(indicator in self.filename for indicator in Q3):
            self.addMonth('SEP')
        elif any(indicator in self.filename for indicator in Q4):
            self.addMonth('DEC')

        self.df.columns = constants.ChurnDataColumns

        self.checkPercents(constants.ChurnDataPercentColumns)

        self.addAdditionalPercentages()

    def addAdditionalPercentages(self):
        """These are figures we precompute for a better user experience"""
        self.df['pct_apps_rcvd_from_this_county'] = 0.0
        total = self.df['snap_apps_rcvd'].where(self.df['county'] == 'California')[0]
        self.df['pct_apps_rcvd_from_this_county'] = self.df['snap_apps_rcvd'] / total

        self.df['pct_cases_sched_recert_this_county'] = 0.0
        total = self.df['cases_sched_recert'].where(self.df['county'] == 'California')[0]
        self.df['pct_cases_sched_recert_this_county'] = \
            self.df['cases_sched_recert'] / total


class DataDashboardAnnualFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DataDashboardAnnualFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers(startCol=4)

        self.addMonth('DEC')

        self.df.columns = constants.DataDashboardAnnualColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')

        self.checkPercents(constants.DataDashboardPercentColumns)


class DataDashboardQuarterlyFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DataDashboardQuarterlyFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers(startCol=3)

        self.df.columns = constants.DataDashboardQuarterlyColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df['month'] = self.df.quarter.str[:3].str.upper()

        self.checkPercents(constants.DataDashboardPercentColumns)


class DataDashboardMonthlyFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DataDashboardMonthlyFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers(startCol=6)

        self.df.columns = constants.DataDashboardMonthlyColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df.month = self.df.month.str[:3].str.upper()

        self.checkPercents(constants.DataDashboardPercentColumns)


class DataDashboard3MthFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DataDashboard3MthFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers(startCol=3)

        self.df.columns = constants.DataDashboard3MthColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df.month = self.df.month.str[:3].str.upper()

        self.checkPercents(constants.DataDashboardPercentColumns)


class DataDashboardPRIRawFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DataDashboardPRIRawFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers(startCol=7)
        # This file is only updated at the end of the year
        self.addMonth('DEC')

        self.df.columns = constants.DataDashboardPRIRawColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')

        self.checkPercents(constants.DataDashboardPercentColumns)


class DFA256Factory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        # drop columns with data we don't need
        self.df.drop(
            [
                self.df.columns[0],
                self.df.columns[2],
                self.df.columns[3],
                self.df.columns[4],
                self.df.columns[5],
            ],
            axis=1,
            inplace=True,
        )
        super(DFA256Factory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        # dates in this column come in excel number format
        date_info = [
            xldate_as_datetime(xldate, 0) for xldate in self.df[self.df.columns[1]]
        ]

        self.df['year'] = [pydate.strftime('%Y').upper() for pydate in date_info]
        self.df['month'] = [pydate.strftime('%b').upper() for pydate in date_info]

        self.df.drop(self.df.columns[1], axis=1, inplace=True)
        # some logic for determining columns in the file based on date follows...
        if self.df.year.unique()[0] == 2002 or \
                (self.df.year.unique()[0] == 2003 and
                    self.df.month.unique()[0] in ['JAN', 'FEB', 'MAR']):
            self.df.columns = constants.DFA256Columns1

        elif self.df.year.unique()[0] == 2003 and \
                self.df.month.unique()[0] in \
                ['APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT']:
            self.df.columns = constants.DFA256Columns2

        else:
            self.df.columns = constants.DFA256Columns3
        # we precompute this for ease of user analysis
        self.df['total_households'] = (
            self.df.num_hh_pub_asst_fed +
            self.df.num_hh_pub_asst_fed_st +
            self.df.num_hh_pub_asst_st +
            self.df.num_hh_nonpub_asst_fed +
            self.df.num_hh_nonpub_asst_fed_st +
            self.df.num_hh_nonpub_asst_st
        )
        # this is also something we precompute for users
        self.df['big_six'] = 0
        self.df = self.df.sort_values(by='total_households', ascending=False)
        self.df = self.df.reset_index(drop=True)
        i = 1
        while i < 7:
            self.df.at[i, 'big_six'] = 1
            i += 1


class DFA296XFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DFA296XFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-13:-10])
        # some logic for determining columns in the file based on date follows...
        if self.df.year.unique()[0] < 2004 or \
                (self.df.year.unique()[0] == 2004 and
                    self.df.month.unique()[0] in ['JAN', 'APR', 'JUL']):
            self.df.columns = constants.DFA296XColumns1

        elif (self.df.year.unique()[0] == 2004 and
                self.df.month.unique()[0] == 'OCT') or \
                (self.df.year.unique()[0] in
                    [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012])\
                or (self.df.year.unique()[0] == 2013 and
                    self.df.month.unique()[0] in ['JAN', 'APR']):
            self.df.columns = constants.DFA296XColumns2

        else:
            self.df.columns = constants.DFA296XColumns3


class DFA358FFactory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(DFA358FFactory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-9:-6])

        if self.df.year.unique()[0] < 2007:
            self.df.columns = constants.DFA358Columns1
        else:
            self.df.columns = constants.DFA358Columns2


class DFA358SFactory(DFA358FFactory):
    def __init__(self):
        super(DFA358SFactory, self).__init__()


class Stat47Factory(FileFactory):

    def build(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(Stat47Factory, self).build()

    def buildSpecific(self):
        self.checkNumbers()
        self.addYear(self.filename[25:27])
        self.addMonth(self.filename[18:21])

        if '(Items 1-14)' in self.filename:
            self.df.columns = constants.Stat47Columns1
        else:
            self.df.columns = constants.Stat47Columns2