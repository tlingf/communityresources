""" Merges cdc and open211 data.
Would use pandas but haven't set that up on this machine.
This is not optimized, but it's a one-time quick run"""

import os
import csv
import re

fn1 = 'dc-open-data-merged-list.csv'
fn2 = '211.csv'

data_merge = list(csv.DictReader(open(fn1, 'rU')))
data_full = csv.DictReader(open(fn2, 'rU'))
keys = data_full.fieldnames
data_full = list(data_full)

matches = 0
count = 0
for row in data_full:
    count += 1
    if row['PublicName'] != "":
        # Remomve symbols and make lower
        name = re.sub(r'[^\w]', ' ', row['PublicName'].lower())
        # Change multiple spaces to one
        name = re.sub(' +',' ', name).strip()

        # data_merge.seek(0)
        for mrow in data_merge:
            
            merge_name = re.sub(r'[^\w]', ' ', mrow['name'].lower())
            merge_name = re.sub(' +',' ',merge_name).strip()
            # print merge_name
            
            if merge_name == name:
                matches += 1
                print "Match",  mrow['name']
                row['990 EIN'] = mrow['ein']
                row['990 Name'] = mrow['name']
                row['Match Type'] = "Character Exact"

            # or beginning of string match 
            elif merge_name[:len(name)] == name or name[:len(merge_name)] == merge_name:
                row['990 EIN'] = mrow['ein']
                row['990 Name'] = mrow['name']
                row['Match Type'] = "Beginning"


added_fields = ["Match Type", "990 Name", "990 EIN"]
keys = added_fields + keys
f = open('merge_990_output.csv', 'wb')
dict_writer = csv.DictWriter(f, keys)
dict_writer.writer.writerow(keys)
dict_writer.writerows(data_full)

print matches

