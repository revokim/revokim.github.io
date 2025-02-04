import csv

input_file = 'kanji_test.csv'
output_file = 'kanji_test_origin.csv'

with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        writer.writerow([row[0]])