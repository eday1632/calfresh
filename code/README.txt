check the following addresses for new files:
http://www.cdss.ca.gov/inforesources/Research-and-Data/CalFresh-Data-Tables
http://www.cdss.ca.gov/inforesources/CalFresh-Resource-Center/Data

update the OUTPATH in data_processor.py and mkdir the directory required

to upload processed files to the server, execute the following line in the terminal:
scp -r <path to latest OUTPUT folder>* eday@45.55.239.171:/home/eday

to upload this data to the calfreshdb, ssh into the server and execute the statements in mysql_statements.txt

update the dates next to the table names in mysql_statements.txt after uploading new files
