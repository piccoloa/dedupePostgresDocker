import csv
import re
import os

import psycopg2
import logging

input_file = 'csv_example_messy_input.csv'

results = []


input_file = 'csv_example_messy_input.csv'

results = []


con = psycopg2.connect("dbname='test' user='postgres' host='pg_test' password='example'")
print('connected to database')
cur = con.cursor()
with open(input_file) as f:
    reader = csv.reader(f)
    for row in reader:
        #results.append(row)
        print(row)
