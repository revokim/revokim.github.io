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

    try:
        kanji_element = soup.select_one('#head > h2 > a')
        if kanji_element:
            kanji = kanji_element.text
            kanji = kanji.split('「')[1].split('」')[0]
            data['한자'] = kanji
        else:
            data['한자'] = 'N/A'

        meaning_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li > span')
        if meaning_element:
            meaning = meaning_element.text
            try:
                meaning = meaning.split('"')[1]
            except IndexError:
                meaning = 'N/A'
        else:
            meaning = 'N/A'
        data['의미'] = meaning

        eumdok_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li:nth-child(2) > span')
        if eumdok_element:
            eumdok = eumdok_element.text
            eumdok = "".join(re.findall(r'[\u30A0-\u30FF、]+', eumdok))
            data['음독'] = eumdok
        else:
            data['음독'] = 'N/A'

        hundok_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > ul > li:nth-child(3) > span')
        if hundok_element:
            hundok = hundok_element.text
            hundok = "".join(re.findall(r'[\u3040-\u309F、]+', hundok))
            data['훈독'] = hundok
        else:
            data['훈독'] = 'N/A'

        eumdok_word_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > h4')
        if eumdok_word_element:
            eumdok_word_element = eumdok_word_element.find_next('ul')
            if eumdok_word_element:
                eumdok_word = re.sub(r'<.*?>', '', str(eumdok_word_element))
                eumdok_word = re.sub(r'[^\u3131-\u3163\uAC00-\uD7A3\u3040-\u309F\u4E00-\u9FFF\s\W]+', '', eumdok_word)
                eumdok_word = re.sub(r'\n', ', ', eumdok_word).strip(', ')
                eumdok_word = re.sub(r'\s{2,}', ' ', eumdok_word).strip()
                eumdok_word = format_string(eumdok_word)
        data['음독 대표단어'] = eumdok_word

        hundok_word_element = soup.select_one('#article-view > div.tt_article_useless_p_margin.contents_style > h4:nth-of-type(2)')
        if hundok_word_element:
            hundok_word_element = hundok_word_element.find_next('ul')
            if hundok_word_element:
                hundok_word_element = ''.join([str(tag) for tag in hundok_word_element.find_all('li')])
                hundok_word_element = re.findall(r'<ruby>(.*?)</span>', hundok_word_element, re.DOTALL)
                hundok_word_element = ' '.join(hundok_word_element)

                hundok_word = re.sub(r'<.*?>', '', str(hundok_word_element))
                hundok_word = re.sub(r'[^\u3131-\u3163\uAC00-\uD7A3\u3040-\u309F\u4E00-\u9FFF\s\W]+', '', hundok_word)
                hundok_word = re.sub(r'\n', ', ', hundok_word).strip(', ')
                hundok_word = re.sub(r'\s{2,}', ' ', hundok_word).strip()
                hundok_word = format_string(hundok_word)
        data['훈독 대표단어'] = hundok_word

    except Exception as e:
        print(f"Error processing {url}: {e}")

    print(data['한자'])
    print(data['의미'])
    print(data['음독'])
    print(data['훈독'])
    print(data['음독 대표단어'])
    print(data['훈독 대표단어'])
    
    return data

output_filename = 'nihongokanji.csv'

with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['한자', '의미', '음독', '훈독', '음독 대표단어', '훈독 대표단어']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for i in range(109, 209):
        url = f"https://nihongokanji.com/{i}"
        print(f"Processing {url}...")
        try:
            data = extract_data(i)
            writer.writerow(data)
            time.sleep(0.5)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            writer.writerow({
                '한자': data.get('한자', 'N/A'),
                '의미': data.get('의미', 'N/A'),
                '음독': data.get('음독', 'N/A'),
                '훈독': data.get('훈독', 'N/A'),
                '음독 대표단어': data.get('음독 대표단어', 'N/A'),
                '훈독 대표단어': data.get('훈독 대표단어', 'N/A')
            })

print(f"CSV 파일 '{output_filename}'이 생성되었습니다.")