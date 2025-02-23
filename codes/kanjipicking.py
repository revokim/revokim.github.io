import csv
import random
import os

def list_words_from_csv(file_path):
    kun_readings = []
    on_readings = []

    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            kun_readings.extend(row['훈독 대표단어'].split(','))
            on_readings.extend(row['음독 대표단어'].split(','))

    return kun_readings, on_readings

file_path = 'nihongokanji.csv'
kun_readings, on_readings = list_words_from_csv(file_path)

all_readings = kun_readings + on_readings

def pick_random_readings(readings, n):
    return random.sample(readings, n)

n = int(input("Enter the number of readings to pick: "))
random_readings = pick_random_readings(all_readings, n)
print(random_readings)

def create_unique_filename(base_name, extension):
    counter = 1
    filename = f"{base_name}.{extension}"
    while os.path.exists(filename):
        filename = f"{base_name}.{extension}"
        counter += 1
    return filename

filename = create_unique_filename("kanji_test", "csv")

with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["한자", "히라가나", "한글"])
    for reading in random_readings:
        parts = reading.split()
        if len(parts) == 3:
            kanji, hiragana, hangul = parts
            writer.writerow([kanji, hiragana, hangul])
        else:
            print(f"Skipping invalid reading: {reading}")

print(f"File {filename} created successfully.")