import csv
import re
import time
import requests
from bs4 import BeautifulSoup

ruby_pattern = re.compile(r'<ruby>(.*?)<rt>(.*?)</rt></ruby>')

def process_item(item):
    matches = ruby_pattern.findall(item)
    base_text = ''.join(m[0] for m in matches)
    reading_text = ''.join(m[1] for m in matches)
    korean = ruby_pattern.sub('', item).strip()
    return f"{base_text} {reading_text} {korean}"

def format_string(input_str):
    groups = input_str.split(',')
    formatted_groups = []

    for group in groups:
        group = group.strip()
        if ' ' in group:
            japanese, korean = group.rsplit(' ', 1)
        else:
            japanese = group
            korean = ''

        kanji = ''
        furigana = ''
        for ch in japanese:
            if '\u4e00' <= ch <= '\u9fff':
                kanji += ch
            elif '\u3040' <= ch <= '\u309f':
                furigana += ch
            else:
                pass

        formatted_group = f"{kanji} {furigana} {korean}"
        formatted_groups.append(formatted_group)


    return ', '.join(formatted_groups)

def extract_data(url_i):
    url = f"https://nihongokanji.com/{url_i}"
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    data = {
        '한자': '',
        '의미': '',
        '음독': '',
        '훈독': '',
        '음독 대표단어': '',
        '훈독 대표단어': ''
    }

    kanji = soup.select_one('#head > h2 > a').text
    kanji = kanji.split('「')[1].split('」')[0]
    data['한자'] = kanji

    meaning = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li > span')
    meaning = meaning.text
    meaning = meaning.split('"')[1]
    data['의미'] = meaning

    eumdok = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li:nth-child(2) > span')
    eumdok = eumdok.text
    eumdok = "".join(re.findall(r'[\u30A0-\u30FF、]+', eumdok))
    data['음독'] = eumdok

    hundok = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li:nth-child(3) > span')
    hundok = hundok.text
    hundok = "".join(re.findall(r'[\u3040-\u309F、]+', hundok))
    data['훈독'] = hundok

    eumdok_word_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > h4').find_next('ul')

    eumdok_word = re.sub(r'<.*?>', '', str(eumdok_word_element))
    eumdok_word = re.sub(r'[^\u3131-\u3163\uAC00-\uD7A3\u3040-\u309F\u4E00-\u9FFF\s\W]+', '', eumdok_word)
    eumdok_word = re.sub(r'\n', ', ', eumdok_word).strip(', ')
    eumdok_word = re.sub(r'\s{2,}', ' ', eumdok_word).strip()
    eumdok_word = format_string(eumdok_word)
    data['음독 대표단어'] = eumdok_word

    hundok_word_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > h4:nth-of-type(2)').find_next('ul')

    hundok_word_element = ''.join([str(tag) for tag in hundok_word_element.find_all('li')])
    hundok_word_element = re.findall(r'<ruby>(.*?)</span>', hundok_word_element, re.DOTALL)
    hundok_word_element = ' '.join(hundok_word_element)
    #print(hundok_word_element)
    #result = ', '.join(process_item(item) for item in hundok_word_element.split(','))
    #print(result)

    hundok_word = re.sub(r'<.*?>', '', str(hundok_word_element))
    hundok_word = re.sub(r'[^\u3131-\u3163\uAC00-\uD7A3\u3040-\u309F\u4E00-\u9FFF\s\W]+', '', hundok_word)
    hundok_word = re.sub(r'\n', ', ', hundok_word).strip(', ')
    hundok_word = re.sub(r'\s{2,}', ' ', hundok_word).strip()
    hundok_word = format_string(hundok_word)
    data['훈독 대표단어'] = hundok_word

    print(kanji)
    print(meaning)
    print(eumdok)
    print(hundok)
    print(eumdok_word)
    print(hundok_word)
    
    return data



output_filename = 'nihongokanji.csv'

with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['한자', '의미', '음독', '훈독', '음독 대표단어', '훈독 대표단어']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for i in range(8, 112):
        url = f"https://nihongokanji.com/{i}"
        print(f"Processing {url}...")
        try:
            data = extract_data(i)
            writer.writerow(data)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing {url}: {e}")

print(f"CSV 파일 '{output_filename}'이 생성되었습니다.")