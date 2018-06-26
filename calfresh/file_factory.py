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
        return CF296Factory(item)
    if item['source'] == 'tbl_churn_data':
        return ChurnDataFactory(item)
    if item['filename'] == 'CFDashboard-Annual.csv':
        return DataDashboardAnnualFactory(item)
    if item['filename'] == 'CFDashboard-Quarterly.csv':
        return DataDashboardQuarterlyFactory(item)
    if item['filename'] == 'CFDashboard-Every_Mth.csv':
        return DataDashboardMonthlyFactory(item)
    if item['filename'] == 'CFDashboard-Every_3_Mth.csv':
        return DataDashboard3MthFactory(item)
    if item['filename'] == 'CFDashboard-PRI_Raw.csv':
        return DataDashboardPRIRawFactory(item)
    if item['source'] == 'tbl_dfa256':
        return DFA256Factory(item)
    if item['source'] == 'tbl_dfa296x':
        return DFA296XFactory(item)
    if item['source'] == 'tbl_dfa358f':
        return DFA358FFactory(item)
    if item['source'] == 'tbl_dfa358s':
        return DFA358SFactory(item)
    if item['source'] == 'tbl_stat47':
        return Stat47Factory(item)

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

    def __init__(self, item):
        self.filename = item['filename']
        self.df = pd.read_csv(item['path'])
        if self.df.empty:
            raise ValueError
        super(FileFactory, self).__init__()

    def __str__(self):
        """Returns the first ten rows of the df attribute"""
        return str(self.df.head(10))

    def build(self):
        self.trim_bogus_rows()
        self.trim_bogus_columns()

        self.check_counties()

        self.build_specific()

        self.df = self.df.fillna(value='\N')

        self.add_quarter()
        self.add_full_date()

    @abstractmethod
    def build_specific(self):
        """Process class specific info, such as column names, year, month, etc."""
        return

    def add_full_date(self):
        """Convert the month and year to valid datetime"""
        self.df['fulldate'] = self.df.month + '/' + self.df.year.map(str)
        self.df.fulldate = pd.to_datetime(self.df.fulldate)

    def add_year(self, year):
        """Add the year to the df

        Args:
            year (str): is passed in as a slice of the filename

        Sets:
            df['year'] (pandas Series): creates the year column
             and sets its value

        Raises:
            ValueError: If the year is earlier than 2002 or later than 2019

        """
        if int('20' + year) > 2019 or int('20' + year) < 2002:
            logging.error('Bad year value: %s', year)
            raise ValueError

        self.df['year'] = int('20' + year)

    def add_month(self, month):
        """Month is passed in as a string or slice of the filename"""
        self.df['month'] = month.upper()

    def add_quarter(self):
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

    def check_numbers(self, startCol=1):
        """Check the type of all values in the input columns

        Args:
            startCol (int): the first column to start looking for, enforcing numerics

        Outputs:
            A squeaky clean set of columns filled with numeric or None values

        """
        for col in self.df.columns[startCol:]:
            i = 0
            for row in self.df[col]:
                self.df.loc[i, col] = self._get_valid_number(row)
                i += 1

    def _get_valid_number(self, num):
        """Extract a number from the input arg or return None

        Args:
            num (str): a value from a cell assumed to contain numeric values

        Returns:
            float or None: float if there were numeric values in the arg,
            or None if it was just junk

        """
        if num is None:
            return np.nan

        try:
            return float(num)
        except ValueError:
            return self._convert_to_number(num)

    def _convert_to_number(self, num):
        """Remove all non-numeric characters from the input

        Args:
            num (str): a string representation of a number

        Returns:
            float stripped of all non-numerics or None

        """
        if num is None:
            return np.nan

        temp = num
        for c in temp:
            if c not in digits + '.':
                num = num.replace(c, '')

        try:
            return float(num)
        except ValueError:
            return np.nan

    def check_percents(self, cols):
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

    def check_counties(self, col=0):
        """Make sure all counties are present

        This function checks that all counties are there and if any are misspelled
        it tries to identify which county it might be

        Args:
            col (int): the column to scan for county names

        Raises:
            ValueError if after its best effort a county is still missing

        """
        # get the string value of the column name
        col = self.df.columns[col]

        self._clean_county_names(col)

        self.df[col] = self.df[col].replace({'Statewide': 'California'})

        self._trim_noncounty_rows(col)
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

    def _trim_noncounty_rows(self, col):
        """Remove any blank row from the county column

        Args:
            col (str): the column with observable county names

        """
        self.df = self.df.dropna(subset=[col]).reset_index(drop=True)

    def _clean_county_names(self, col):
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
                    closest = self._get_closest_spelled_county(county)
                    self.df.loc[i, col] = closest
                else:
                    self.df.loc[i, col] = np.nan
            i += 1

    def _get_nearest_spelled_counties(self, county):
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

    def _get_closest_spelled_county(self, county):
        """Get the county with the smallest edit distance or None

        Args:
            county (str): invalid county name to replace

        Returns:
            A valid county name or None if there were none within 3 edits

        """
        potentials = self._get_nearest_spelled_counties(county)
        if not potentials:
            return np.nan

        closest = min(potentials, key=potentials.get)
        # Needs to have fewer than three edits made
        if potentials[closest] < 3L:
            return constants.county_dict[closest]
        else:
            return np.nan

    def trim_bogus_columns(self):
        """Drop columns off the end of the table with more than a quarter empty rows"""
        rowcount = self.df.shape[0] / 4
        while self.df[self.df.columns[-1]].isnull().sum() > rowcount:
            self.df.drop(self.df.columns[-1], axis=1, inplace=True)

    def trim_bogus_rows(self):
        """Drop rows off the bottom of the table with more than half empty columns"""
        colcount = self.df.shape[1] / 2
        while self.df.iloc[-1].isnull().sum() > colcount:
            self.df.drop(self.df.index[-1], inplace=True)


class CF296Factory(FileFactory):

    def build(self):
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

    def build_specific(self):
        self.check_numbers()
        # dates in this column come in excel number format
        date_info = [
            xldate_as_datetime(xldate, 0) for xldate in self.df[self.df.columns[1]]
        ]

        self.df['year'] = [pydate.strftime('%Y').upper() for pydate in date_info]
        self.df['month'] = [pydate.strftime('%b').upper() for pydate in date_info]

        self.df.drop(self.df.columns[1], axis=1, inplace=True)
        self.df.columns = constants.CF296Columns


class ChurnDataFactory(FileFactory):

    def build_specific(self):
        self.check_numbers()
        if self.filename[0] in digits:
            self.add_year(self.filename[2:4])
        else:
            self.add_year(self.filename[4:6])

        Q1 = ['Q1', 'JAN']
        Q2 = ['Q2', 'APRIL']
        Q3 = ['Q3', 'JUL']
        Q4 = ['Q4', 'OCT']

        if any(indicator in self.filename for indicator in Q1):
            self.add_month('MAR')
        elif any(indicator in self.filename for indicator in Q2):
            self.add_month('JUN')
        elif any(indicator in self.filename for indicator in Q3):
            self.add_month('SEP')
        elif any(indicator in self.filename for indicator in Q4):
            self.add_month('DEC')

        self.df.columns = constants.ChurnDataColumns

        self.check_percents(constants.ChurnDataPercentColumns)

        self.add_additional_percentages()

    def add_additional_percentages(self):
        """These are figures we precompute for a better user experience"""
        self.df['pct_apps_rcvd_from_this_county'] = 0.0
        total = self.df['snap_apps_rcvd'].where(self.df['county'] == 'California')[0]
        self.df['pct_apps_rcvd_from_this_county'] = self.df['snap_apps_rcvd'] / total

        self.df['pct_cases_sched_recert_this_county'] = 0.0
        total = self.df['cases_sched_recert'].where(self.df['county'] == 'California')[0]
        self.df['pct_cases_sched_recert_this_county'] = \
            self.df['cases_sched_recert'] / total


class DataDashboardAnnualFactory(FileFactory):

    def build_specific(self):
        self.check_numbers(startCol=4)

        self.add_month('DEC')

        self.df.columns = constants.DataDashboardAnnualColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')

        self.check_percents(constants.DataDashboardPercentColumns)


class DataDashboardQuarterlyFactory(FileFactory):

    def build_specific(self):
        self.check_numbers(startCol=3)

        self.df.columns = constants.DataDashboardQuarterlyColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df['month'] = self.df.quarter.str[:3].str.upper()

        self.check_percents(constants.DataDashboardPercentColumns)


class DataDashboardMonthlyFactory(FileFactory):

    def build_specific(self):
        self.check_numbers(startCol=6)

        self.df.columns = constants.DataDashboardMonthlyColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df.month = self.df.month.str[:3].str.upper()

        self.check_percents(constants.DataDashboardPercentColumns)


class DataDashboard3MthFactory(FileFactory):

    def build_specific(self):
        self.check_numbers(startCol=3)

        self.df.columns = constants.DataDashboard3MthColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')
        self.df.month = self.df.month.str[:3].str.upper()

        self.check_percents(constants.DataDashboardPercentColumns)


class DataDashboardPRIRawFactory(FileFactory):

    def build_specific(self):
        self.check_numbers(startCol=7)
        # This file is only updated at the end of the year
        self.add_month('DEC')

        self.df.columns = constants.DataDashboardPRIRawColumns

        self.df.year = pd.to_numeric(self.df.year, downcast='integer')

        self.check_percents(constants.DataDashboardPercentColumns)


class DFA256Factory(FileFactory):

    def build(self, item):
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

    def build_specific(self):
        self.check_numbers()
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

    def build_specific(self):
        self.check_numbers()
        self.add_year(self.filename[-6:-4])
        self.add_month(self.filename[-13:-10])
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

    def build_specific(self):
        self.check_numbers()
        self.add_year(self.filename[-6:-4])
        self.add_month(self.filename[-9:-6])

        if self.df.year.unique()[0] < 2007:
            self.df.columns = constants.DFA358Columns1
        else:
            self.df.columns = constants.DFA358Columns2


class DFA358SFactory(DFA358FFactory):
    def __init__(self, item):
        super(DFA358SFactory, self).__init__(item)


class Stat47Factory(FileFactory):

    def build_specific(self):
        self.check_numbers()
        self.add_year(self.filename[25:27])
        self.add_month(self.filename[18:21])

        if '(Items 1-14)' in self.filename:
            self.df.columns = constants.Stat47Columns1
        else:
            self.df.columns = constants.Stat47Columns2
