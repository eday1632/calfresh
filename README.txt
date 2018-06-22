===========
CalFreshDB
===========

This project provides access to CalFresh's nutrition assistance data through a MySQL database. We download the latest data, clean it, and upload it to the database. Support for the project is provided through Sacremento State University.

There are three main services:
    WebCrawler
    Worker
    DataLoader

WebCrawler uses a PageParser to retrieve HTML files from the CDSS websites containing
URLs to Excel files containing CalFresh data. URLs for new and updated files are used
to download the new files, which get saved to the file system (S3 would also work).

A Worker then gets called and passed the name of a table with new data. It extracts
the data from Excel into a pandas dataframe, cleans and transforms the data, and
then exports the dataframes into CSV files stored on the file system (or S3).

A DataLoader is called and passed the path to the directory containing the day's new
data to load. It makes a system call that uses mysqlimport to load each new file.

