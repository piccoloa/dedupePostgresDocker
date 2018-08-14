import csv
import re
import os

import psycopg2
import logging

mode = 'development'
#mode = 'production'
log_file = 'writeCSVtoPostgres.log'

if mode == 'development':
    log_level = logging.DEBUG
    log_mode = 'w'
else:
    log_level = logging.WARNING
    log_mode = 'a'
# Create a logger
logger = logging.getLogger(__name__) #
logger.setLevel(logging.INFO) #

# Create a file handler that logs into a file into the current folder
logfile = os.path.join(os.path.dirname(os.path.realpath(__file__)),log_file) #
handler = logging.FileHandler(logfile, mode=log_mode) #
handler.setLevel(log_level)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') #
handler.setFormatter(formatter) #

# Attach the handler to the logger
logger.addHandler(handler) #

input_file = 'csv_example_messy_input.csv'

results = []

while True:
    try:
        con = psycopg2.connect("dbname='test' user='postgres' host='pg_test' password='example'")
        logger.info('connected to database')
        cur = con.cursor()
        with open(input_file) as f:
            reader = csv.reader(f)
            #print(reader)
            heading_row = next(reader)
            #[print(x) for x in heading_row]
            #print(heading_row)
            #heading_row = heading_row.next(f)
            '''creating a list from header and cleaning lower case'''
            heading_row = [re.sub(" ","_",x.lower()) for x in heading_row]
            num_cols = len(heading_row)
            #print(num_cols)
            # '''creating a tupple for col names'''
            mog = "(" + ("%s,"*(num_cols -1)) + "%s)"
            #print("mog worked", mog)

            #Query to get a list of reserved keywords to compare with header/column names
            cur.execute("select word from pg_get_keywords() where catdesc = 'reserved'")
            reserved = cur.fetchall()
            reserved = [x[0] for x in reserved]
            #Compare the column names in heading_row to reserved keywords to make sure there are no conflicts
            #and add "_" to any that do use reserved keywords
            heading_row = [(i+"_") if i in reserved else i for i in heading_row]
            #print(heading_row)
            cur.execute('drop table if exists csv_messy_data')

            cur.execute('create table csv_messy_data (%s)'%','.join('%s varchar(200)' % name for name in heading_row))
            con.commit()
        #print("created table")
        logger.info('created table in db')
        with open(input_file) as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                results.append(row)
            #print(results)
            #print(results)
            args_str = ','.join(cur.mogrify(mog,x).decode('utf8') for x in results)
            #print(args_str)
            header = "("+ ','.join(x for x in heading_row) +")"
            #print(header)
            cur.execute("insert into csv_messy_data %s values %s" % (header, args_str))
            con.commit()
            con.close()
        logger.info('data written to new table')

        #logger.info('created table in db')
        break
    except Exception as e:
        print('failed to connect {}'.format(e))
        logger.error('databases connection failed {}'.format(e))
        break
