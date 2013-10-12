import os
import csv
import re

fn1 = 'dc-open-data-merged-list.csv'
fn2 = '211.csv'

data_merge = list(csv.DictReader(open(fn1, 'rU')))
data_full = list(csv.DictReader(open(fn2, 'rU')))

matches = 0
count = 0
for row in data_full:
    count += 1
    if count < 20:
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
                row['EIN'] = mrow['ein']
                row['990 Name'] = mrow['name']
                row['Match Type'] = "Character Exact"

            # or beginning of string match 
            elif merge_name[:len(name)] == name or name[:len(merge_name)] == merge_name:
                row['EIN'] = mrow['ein']
                row['990 Name'] = mrow['name']
                row['Match Type'] = "Beginning"


keys = data_full[0].keys()
f = open('cdc_output.csv', 'wb')
dict_writer = csv.DictWriter(f, keys)
dict_writer.writer.writerow(keys)
dict_writer.writerows(data_full)

print matches

