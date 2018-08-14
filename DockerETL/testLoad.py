#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a setup script for mysql_example.  It downloads a zip file of
Illinois campaign contributions and loads them in t aMySQL database
named 'contributions'.

__Note:__ You will need to run this script first before execuing
[mysql_example.py](http://datamade.github.com/dedupe-examples/docs/mysql_example.html).

Tables created:
* raw_table - raw import of entire CSV file
* donors - all distinct donors based on name and address
* recipients - all distinct campaign contribution recipients
* contributions - contribution amounts tied to donor and recipients tables
"""
import csv
import os
import zipfile

import dj_database_url
import psycopg2
import psycopg2.extras
import unidecode
import requests

_file = 'Illinois-campaign-contributions'
contributions_zip_file = _file + '.txt.zip'
contributions_txt_file = _file + '.txt'
contributions_csv_file = _file + '.csv'

if not os.path.exists(contributions_zip_file):
    print('downloading', contributions_zip_file, '(~60mb) ...')
    u = requests.get(
        'https://s3.amazonaws.com/dedupe-data/Illinois-campaign-contributions.txt.zip')
    localFile = open(contributions_zip_file, 'wb')
    localFile.write(u.content)
    localFile.close()

if not os.path.exists(contributions_txt_file):
    zip_file = zipfile.ZipFile(contributions_zip_file, 'r')
    print('extracting %s' % contributions_zip_file)
    zip_file_contents = zip_file.namelist()
    for f in zip_file_contents:
        if ('.txt' in f):
            zip_file.extract(f)
    zip_file.close()

# Create a cleaned up CSV version of file with consistent row lengths.
# Postgres COPY doesn't handle "ragged" files very well
if not os.path.exists(contributions_csv_file):
    print('converting tab-delimited raw file to csv...')
    with open(contributions_txt_file, 'rU') as txt_file, \
            open(contributions_csv_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        for line in txt_file:
            if not all(ord(c) < 128 for c in line):
                line = unidecode.unidecode(line)
            row = line.rstrip('\t\r\n').split('\t')
            if len(row) != 29:
                print('skipping bad row (length %s, expected 29):' % len(row))
                print(row)
                continue
            csv_writer.writerow(row)


db_conf = dj_database_url.config()

# if not db_conf:
#     raise Exception(
#         'set DATABASE_URL environment variable with your connection, e.g. '
#         'export DATABASE_URL=postgres://user:password@host/mydatabase'
#     )
