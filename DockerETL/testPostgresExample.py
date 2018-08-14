# -*- coding: utf-8 -*-
"""
Revised script to work in docker environment original
from https://github.com/dedupeio/dedupe-examples/tree/master/pgsql_example
 @author: nathanhoeft.

This is an example of using dedupe.match againsts a dataset from a postgresql table.
For larger datasets, please see the mysql example.

__Note:__ You will need to run the writeCSVtoPostgres.py script before executing this script.
"""
import sys

import dedupe
import os
import re
import collections
import time

import psycopg2 as psy
import psycopg2.extras
from unidecode import unidecode

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

# Input settings
settings_file = 'postgres_settings'
training_file = 'postgres_training.json'

# Start the timer and lets get this show on the road
start_time = time.time()

while True:
    try:
        con = psy.connect("dbname='test' user='postgres' host='pg_test' password='example'")
        con2 = psy.connect(database='test', user = 'postgres', host='pg_test', password='example')
        c = con.cursor(cursor_factory=psy.extras.RealDictCursor)
        logger.info('connected to DB...')
        MAILING_SELECT = 'SELECT id,site_name, address, zip, phone FROM csv_messy_data'
        logger.debug('MAILING_SELECT statement: {}'.format(MAILING_SELECT))
        break
    except Exception as e:
        logger.error('Failed to connect to DB: {}'.format(e))
        logger.debug('Full stack trace\n{}'.traceback.format_exc())
        break

def preProcess(column):
    try : # python 2/3 string differences
        column = column.decode('utf8')
    except AttributeError:
        pass
    column = unidecode(column)
    column = re.sub('  +', ' ', column)
    column = re.sub('\n', ' ', column)
    column = column.strip().strip('"').strip("'").lower().strip()
    if not column :
        column = None
    return column

while True:
    try:
        logger.info('importing data ...')
        c.execute(MAILING_SELECT)
        data = c.fetchall()
        logger.info('data imported')
        data_d = {}
        for row in data:
            clean_row = [(k, preProcess(v)) for (k, v) in row.items()]
            row_id = int(row['id'])
            data_d[row_id] = dict(clean_row)
        logger.info('created data_d[row_id]')

        if os.path.exists(settings_file):
            logger.info('reading from {}'.format(settings_file))
            with open(settings_file) as sf :
                deduper = dedupe.StaticDedupe(sf)
                logger.info('StaticDedupe ran')

        else:
            fields = [
                {'field' : 'site_name', 'type': 'String'},
                {'field' : 'address', 'type': 'String'},
                {'field' : 'zip', 'type': 'String', 'has missing' : True},
                {'field' : 'phone', 'type': 'String', 'has missing' : True},
                ]

            deduper = dedupe.Dedupe(fields)
            logger.info('Dedupe(fields ok)')

            deduper.sample(data_d, 150000)
            logger.info('deduper sample sample run')

            if os.path.exists(training_file):
                logger.info('reading labeled examples from {}'.format(training_file))
                with open(training_file) as tf :
                    deduper.readTraining(tf)
            logger.info('deduper readTraning ran')

            logger.info('starting acriver labeling ...')

            dedupe.consoleLabel(deduper)
            logger.info('consoleLabel ran')

            deduper.train()
            logger.info('dedupe.train ran')

            with open(training_file, 'w') as tf :
                deduper.writeTraining(tf)
            logger.info('deduper.writeTraining ran')

            with open(settings_file, 'w') as sf :
                deduper.writeSettings(sf)
            logger.info('dedupe.writeSettings ran')

            logger.info('blocking...')

            threshold = deduper.threshold(data_d, recall_weight=2)
            logger.info('threshold created')

            logger.info('clustering...')
            clustered_dupes = deduper.match(data_d, threshold)
            logger.info('cluster_dupes created.')

            logger.info('# duplicate sets {}'.format(str(len(clustered_dupes))))

            c2 = con2.cursor()
            logger.info('c2 connected')
            c2.execute('SELECT * FROM csv_messy_data')
            logger.info('c2.execute select csv_messy_data ran')
            data = c2.fetchall()
            logger.info('data from c2.fetchall ran')

            full_data = []

            cluster_membership = collections.defaultdict(lambda : 'x')
            logger.info('cluster_membership created')
            for cluster_id, (cluster, score) in enumerate(clustered_dupes):
                for record_id in cluster:
                    for row in data:
                        if record_id == int(row[0]):
                            row = list(row)
                            row.insert(0,cluster_id)
                            row = tuple(row)
                            full_data.append(row)

            columns = "SELECT column_name FROM information_schema.columns WHERE table_name = 'csv_messy_data'"
            logger.info('columns created')
            c2.execute(columns)
            logger.info('selected columns from db')
            column_names = c2.fetchall()
            logger.info('fetched columns names')
            column_names = [x[0] for x in column_names]
            column_names.insert(0,'cluster_id')
            logger.debug(column_names)

            c2.execute('DROP TABLE IF EXISTS deduped_table')
            logger.info('drop table if exists ran')
            field_string = ','.join('%s varchar(200)' % name for name in column_names)
            logger.info('field_string created')
            c2.execute('CREATE TABLE deduped_table (%s)' % field_string)
            logger.info('created dedupe table')
            con2.commit()
            logger.info('wrote dedupe table to db')

            num_cols = len(column_names)
            mog = "(" + ("%s,"*(num_cols -1)) + "%s)"
            logger.info('mog created')
            args_str = ','.join(c2.mogrify(mog,x).decode('utf8') for x in full_data)
            logger.info('args_str created')
            values = "("+ ','.join(x for x in column_names) +")"
            c2.execute("INSERT INTO deduped_table %s VALUES %s" % (values, args_str))
            logger.info('inserted records to dedupe table')
            con2.commit()
            logger.info('con2 commit records to dedupe table')
            con2.close()
            con.close()

            logger.info('ran in {} "seconds"'.format(time.time() - start_time))

        break

    except Exception as e:
        logger.error('Failure during ETL process {}'.format(e))
        logger.debug('Full stack trace\n{}'.traceback.format_exc())
        break
