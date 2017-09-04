
"""FileFactory module containing base and subclasses
TODOs:
    Finish documentation
    Build tests
    Possibly refactor for better testing
"""

from string import digits
from abc import ABCMeta, abstractmethod

import pandas as pd
import numpy as np
import editdistance

from constants import constants


def initialize(item):
    """Initializes the proper FileFactory object based on the source directory of the item

        Args:
            item (dict): object with path, source and filename keys

        Returns:
            FileFactory: subclass corresponding to the source of the item

        Raises:
            ValueError: If the source of the item is unknown
    """

    if item['source'] == 'tbl_cf15':
        return CF15Factory(item)
    if item['source'] == 'tbl_cf296':
        return CF296Factory(item)
    if item['source'] == 'tbl_churn_data':
        return ChurnDataFactory(item)
    if item['source'] == 'tbl_data_dashboard':
        return DataDashboardFactory(item)
    if item['source'] == 'tbl_dfa256':
        return DFA256Factory(item)
    if item['source'] == 'tbl_dfa296':
        return DFA296Factory(item)
    if item['source'] == 'tbl_dfa296x':
        return DFA296XFactory(item)
    if item['source'] == 'tbl_dfa358f':
        return DFA358FFactory(item)
    if item['source'] == 'tbl_dfa358s':
        return DFA358SFactory(item)
    if item['source'] == 'tbl_stat47':
        return Stat47Factory(item)
    if item['source'] == 'tbl_stat48':
        return Stat48Factory(item)

    raise ValueError


class FileFactory(object):
    """Base class for all the file factories: CF15Factory, CF296Factory, ChurnDataFactory, DataDashboardFactory, DFA256Factory, DFA296Factory, DFA296XFactory, DFA358FFactory, DFA358SFactory, Stat47Factory, Stat48Factory

    Attributes:
        df (pandas DataFrame): the csv file passed in converted to a pd.DataFrame object
        filename (str): name of the csv file
        constants (obj constants): an object with lists of column names to label the factories' df attributes and a dict of county keys and values
        year (int): the year (yyyy) pertaining to the data within the factory
        quarter (int) the quarter pertaining to the data within the factory
        month (str): the month (MMM) pertaining to the data within the factory


    """
    
    __metaclass__ = ABCMeta


    def __init__(self, item):
        """This function basically calls everything needed to setup the factory and its attributes

        Args:
            item (dict): object with path, source and filename keys

        Raises:
            ValueError: If the DataFrame object is empty, we're in trouble
        """
        super(FileFactory, self).__init__()

        self.df = pd.read_csv(item['path'])
        if self.df.empty: raise ValueError

        self.filename = item['filename']
        self.constants = constants()
        self.year = None
        self.quarter = None
        self.month = None

        self.trimBogusRows()
        self.trimBogusColumns()

        self.checkCounties()

        self.checkNumbers()

        self.buildSpecific() 

        self.addQuarter()
        self.addFullDate()


    def __str__(self):
        """returns the first ten rows of the df attribute"""
        return str(self.df.head(10))


    @abstractmethod
    def buildSpecific(self):
        """process class specific info, such as column names, year, month, etc."""
        return


    def addFullDate(self):        
        """convert the month and year to valid datetime"""
        self.df['fulldate'] = pd.to_datetime(self.month + '/' + str(self.year))
    

    def addYear(self, year):
        """add the year to the df and set the year attribute

        Args:
            year (str): is passed in as a slice of the filename

        Sets:
            df['year'] (pandas Series): creates the year column and sets its value
            year (int): converts the year argument to a number

        Raises:
            ValueError: If the year is earlier than 2002 or later than 2017
        """

        self.year = int('20' + year)
        self.df['year'] = self.year
        
        if self.year > 2017 or self.year < 2002:
            raise ValueError


    def addMonth(self, month):
        """month is passed in as a slice of the filename"""
        self.month = month.upper()
        self.df['month'] = self.month
        
        if self.month not in ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']:
            raise ValueError


    def addQuarter(self):
        """use the month to determine the quarter"""
        if self.month in ['JAN','FEB','MAR']:
            self.df['quarter'] = 1.0
        elif self.month in ['APR','MAY','JUN']:
            self.df['quarter'] = 2.0
        elif self.month in ['JUL','AUG','SEP']:
            self.df['quarter'] = 3.0
        elif self.month in ['OCT','NOV','DEC']:
            self.df['quarter'] = 4.0
        else:
            raise ValueError


    def checkNumbers(self):
        """check the type of all values in the input columns"""
        for col in self.df.columns[1:]:
            i = 0
            for row in self.df[col]:
                self.df.loc[i, col] = self._getValidNumber(row)
                i += 1


    def _getValidNumber(self, num):
        try:
            return float(num)
        except ValueError:
            return self._convertToNumber(num)


    def _convertToNumber(self, num):
        """remove all non-digit chars from the input"""
        temp = num
        for c in temp:
            if c not in digits + '.':
                num = num.replace(c, '')

        # convert the remaining value to a number or NaN
        try:
            return float(num)
        except ValueError:
            return np.nan


    def checkPercents(self, cols):
        for col in cols:
            i = 0
            for row in self.df[col]:
                if row > 1.0 or row < -1.0:
                    self.df.loc[i, col] = row / 100.0
                i += 1


    def checkCounties(self, col=0):
        # get the column name
        col = self.df.columns[col]
        # remove padding and correct misspellings
        self._cleanCountyNames(col)
        # replace Statewide with California to standardize
        self.df[col] = self.df[col].replace({'Statewide':'California'})
        # remove any rows that don't contain a county name
        self._trimNonCountyRows(col)

        # make sure all the counties are present
        if not self._completeCountySet(col):
            raise ValueError


    def _trimNonCountyRows(self, col):
        """remove any blank row from the county column"""
        self.df = self.df.dropna(subset=[col]).reset_index(drop=True)


    def _completeCountySet(self, col):
        # get the reference set and observed set of counties
        reference = set(self.constants.county_dict.values())
        observed = set(self.df[col].values)
        # remove Statewide from the reference set since it was replaced with California
        reference.remove('Statewide')
        # print reference, '\n', observed

        # return the equality of the sets
        return observed == reference


    def _cleanCountyNames(self, col):
        self.df[col] = self.df[col].str.strip()
        i = 0
        for county in self.df[col]:
            if not self._isValidCounty(county):
                if type(county) == str:
                    county = county.replace(' ','')
                    closest = self._getClosestSpelledCounty(county)
                    self.df.loc[i, col] = closest
                else: self.df.loc[i, col] = np.nan
            i += 1


    def _isValidCounty(self, county):
        return county in self.constants.county_dict.keys()


    def _getNearestSpelledCounties(self, county):
        vals = {}
        for key in self.constants.county_dict.keys():
            county = str(county)
            if len(county) < (len(key) + 3) and len(county) > (len(key) - 3):
                vals[key] = editdistance.eval(key, county)

        return vals


    def _getClosestSpelledCounty(self, county):
        potentials = self._getNearestSpelledCounties(county)
        if not potentials: return np.nan

        closest = min(potentials, key=potentials.get)
        
        if potentials[closest] < 3L:
            return self.constants.county_dict[closest]
        else: 
            return np.nan


    def trimBogusColumns(self):
        while self.df[self.df.columns[-1]].isnull().sum() > 50:
            self.df.drop(self.df.columns[-1], 1, inplace=True)
    

    def trimBogusRows(self):
        colcount = self.df.shape[1] / 2
        while self.df.iloc[-1].isnull().sum() > colcount:
            self.df.drop(self.df.index[-1], inplace=True)



class CF15Factory(FileFactory):
    """builds the CF15Factory"""
    def __init__(self, item):
        super(CF15Factory, self).__init__(item)



class CF296Factory(FileFactory):
    """builds the CF296Factory"""
    def __init__(self, item):
        super(CF296Factory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-9:-6])

        self.df.columns = self.constants.CF296Columns



class ChurnDataFactory(FileFactory):
    """builds the ChurnDataFactory"""
    def __init__(self, item):
        super(ChurnDataFactory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[4:6])
        
        if self.filename.endswith('0.csv'):
            self.month = 'MAR'
        elif self.filename.endswith('1.csv'):
            self.month = 'JUN'
        elif self.filename.endswith('2.csv'):
            self.month = 'SEP'
        elif self.filename.endswith('3.csv'):
            self.month = 'DEC'
        
        self.addMonth(self.month)

        self.df.columns = self.constants.ChurnDataColumns

        self.checkPercents(self.constants.ChurnDataPercentColumns)
        
        self.addAdditionalPercentages()


    def addAdditionalPercentages(self):
        self.df['pct_apps_rcvd_from_this_county'] = 0.0
        total = self.df['snap_apps_rcvd'].where(self.df['county'] == 'California')[0]
        self.df['pct_apps_rcvd_from_this_county'] = self.df['snap_apps_rcvd'] / total

        self.df['pct_cases_sched_recert_this_county'] = 0.0
        total = self.df['cases_sched_recert'].where(self.df['county'] == 'California')[0]
        self.df['pct_cases_sched_recert_this_county'] = self.df['cases_sched_recert'] / total



class DataDashboardFactory(FileFactory):
    """builds the DataDashboardFactory"""
    def __init__(self, item):
        super(DataDashboardFactory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-8:-6])
        self.addMonth(self.filename[-11:-8])

        self.df.columns = self.constants.DataDashboardColumns

        self.checkPercents(self.constants.DataDashboardPercentColumns)

        

class DFA256Factory(FileFactory):
    """builds the DFA256Factory"""
    def __init__(self, item):
        super(DFA256Factory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-9:-6])

        if self.year == 2002 or (self.year == 2003 and self.month in ['JAN','FEB','MAR']):
            self.df.columns = self.constants.DFA256Columns1

        elif self.year == 2003 and self.month in ['APR','MAY','JUN','JUL','AUG','SEP','OCT']:
            self.df.columns = self.constants.DFA256Columns2

        else:
            self.df.columns = self.constants.DFA256Columns3



class DFA296Factory(FileFactory):
    """builds the DFA296Factory"""
    def __init__(self, item):
        super(DFA296Factory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-9:-6])

        if self.year <= 2011:
            self.df.columns = self.constants.DFA296Columns1
        else:
            self.df.columns = self.constants.DFA296Columns2

        self.sumColumns(self.constants.DFA296SumColumns)


    def sumColumns(self, tuples):
        for tup in tuples:
            if tup[1] in self.df.columns and tup[2] in self.df.columns:
                self.df[tup[0]] = self.df[tup[1]].apply(float) + self.df[tup[2]].apply(float)



class DFA296XFactory(FileFactory):
    """builds the DFA296XFactory"""
    def __init__(self, item):
        super(DFA296XFactory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-13:-10])

        if self.year < 2004 or (self.year == 2004 and self.month in ['JAN','APR','JUL']):
            self.df.columns = self.constants.DFA296XColumns1
        elif (self.year == 2004 and self.month == 'OCT') or (self.year in [2005,2006,2007,2008,2009,2010,2011,2012]) or (self.year == 2013 and self.month in ['JAN','APR']):
            self.df.columns = self.constants.DFA296XColumns2
        else:
            self.df.columns = self.constants.DFA296XColumns3


        
class DFA358FFactory(FileFactory):
    """builds the DFA358FFactory"""
    def __init__(self, item):
        super(DFA358FFactory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[-6:-4])
        self.addMonth(self.filename[-9:-6])

        if self.year < 2007:
            self.df.columns = self.constants.DFA358Columns1
        else:
            self.df.columns = self.constants.DFA358Columns2



class DFA358SFactory(DFA358FFactory):
    """builds the DFA358SFactory"""
    def __init__(self, item):
        super(DFA358SFactory, self).__init__(item)



class Stat47Factory(FileFactory):
    """builds the Stat47Factory"""
    def __init__(self, item):
        super(Stat47Factory, self).__init__(item)


    def buildSpecific(self):
        self.addYear(self.filename[25:27])
        self.addMonth(self.filename[18:21])

        if '(Items 1-14)' in self.filename:
            self.df.columns = self.constants.Stat47Columns1
        else:
            self.df.columns = self.constants.Stat47Columns2



class Stat48Factory(FileFactory):
    """builds the Stat48Factory"""
    def __init__(self, item):
        super(Stat48Factory, self).__init__(item)

        
    def buildSpecific(self):
        self.addYear(self.filename[-8:-6])
        self.addMonth(self.filename[-11:-8])

        self.df.columns = self.constants.Stat48Columns
























        