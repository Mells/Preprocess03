import csv
import pandas as pd

with open("vocabulary_t.csv", 'r') as voc_t, \
        open("vocabulary.csv", 'w') as new_csv:
    voc_reader = csv.reader(voc_t, delimiter=';')
    new_writer = csv.writer(new_csv, delimiter=';')

    header = next(voc_reader)
    new_writer.writerow(header)

    for row in voc_reader:
        #print(row[22])
        new_writer.writerow(row[0:23]+[str(0)]+row[25:])

