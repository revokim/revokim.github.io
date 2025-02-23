import csv
import random
import os

def list_kanji_from_csv(file_path):
    kanji_list = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            kanji_list.append({
                '한자': row['한자'],
                '의미': row['의미'],
                '음독': row['음독'],
                '훈독': row['훈독']
            })

    return kanji_list

def pick_random_kanji(kanji_list, n):
    return random.sample(kanji_list, n)

def create_unique_filename(base_name, extension):
    counter = 1
    filename = f"{base_name}.{extension}"
    while os.path.exists(filename):
        filename = f"{base_name}_{counter}.{extension}"
        counter += 1
    return filename

file_path = 'nihongokanji.csv'
kanji_list = list_kanji_from_csv(file_path)

n = int(input("Enter the number of kanji to pick: "))
random_kanji = pick_random_kanji(kanji_list, n)

filename = create_unique_filename("nihongo_kanji_test", "csv")

with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['한자', '의미', '음독', '훈독'])
    writer.writeheader()
    for kanji in random_kanji:
        writer.writerow(kanji)

print(f"File {filename} created successfully.")