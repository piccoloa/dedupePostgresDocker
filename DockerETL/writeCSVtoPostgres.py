#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a setup script for pgsql_example. It loads the data in a csv file into a
a postgresql table named csv_messy_data.

__Note:__ You will need to run this script first before executing [pgsql_example.py]

Tables created:
* csv_messy_data - raw import of entire CSV file
"""

import csv
import re
import os

import psycopg2

##
## ***Always be logging***
##
import traceback
import logging
from logging.handlers import RotatingFileHandler

# Logging defaults - basic config will log to stdout, then we'll add a log-to-file handler
# Allow log override from environ variable
FILE_LOG_FORMAT = "%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s"
#CONSOLE_LOG_FORMAT = "%(levelname)s %(module)s:%(lineno)d %(message)s"
CONSOLE_LOG_FORMAT = FILE_LOG_FORMAT
LOG_FILENAME = __file__ + '.log'

LOG_LEVEL = os.getenv('LOG_LEVEL', logging.INFO)
if LOG_LEVEL == 'debug':
    LOG_LEVEL=logging.DEBUG

# setup for console
logging.basicConfig(level=LOG_LEVEL, format=CONSOLE_LOG_FORMAT)
logger = logging.getLogger('')

# setup for file
log_file_handler = RotatingFileHandler(LOG_FILENAME, maxBytes=20971520, backupCount=5)
log_file_handler.setFormatter(logging.Formatter(FILE_LOG_FORMAT))
logger.addHandler(log_file_handler)
##
##
##

input_file = 'csv_example_messy_input.csv'

results = []

while True:
    try:
        con = psycopg2.connect("dbname='test' user='postgres' host='pg_test' password='example'")
        logger.info('connected to database')
        cur = con.cursor()
        with open(input_file) as f:
            reader = csv.reader(f)
            logger.debug("csv results", reader)
            heading_row = next(reader)

            '''creating a list from header and cleaning lower case'''
            heading_row = [re.sub(" ","_",x.lower()) for x in heading_row]
            num_cols = len(heading_row)
            logger.debug("number of columsn", num_cols)
            # '''creating a tupple for col names'''
            mog = "(" + ("%s,"*(num_cols -1)) + "%s)"
            logger.debug("mog worked", mog)

            #Query to get a list of reserved keywords to compare with header/column names
            cur.execute("select word from pg_get_keywords() where catdesc = 'reserved'")
            reserved = cur.fetchall()
            reserved = [x[0] for x in reserved]
            #Compare the column names in heading_row to reserved keywords to make sure there are no conflicts
            #and add "_" to any that do use reserved keywords
            heading_row = [(i+"_") if i in reserved else i for i in heading_row]
            logger.debug("heading_row", heading_row)
            cur.execute('drop table if exists csv_messy_data')

            cur.execute('create table csv_messy_data (%s)'%','.join('%s varchar(200)' % name for name in heading_row))
            con.commit()

        logger.info('created table in db')
        with open(input_file) as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                results.append(row)
            args_str = ','.join(cur.mogrify(mog,x).decode('utf8') for x in results)
            header = "("+ ','.join(x for x in heading_row) +")"
            cur.execute("insert into csv_messy_data %s values %s" % (header, args_str))
            con.commit()
            con.close()
        logger.info('data written to new table')
        break
        
    except Exception as e:
        logger.error('Failure during ETL process {}'.format(e))
        logger.debug('Full stack trace\n{}'.traceback.format_exc())
        break
