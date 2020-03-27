import csv, os, sys
import requests
from bs4 import BeautifulSoup


URL = 'https://hh.ru/search/vacancy?area=1&st=searchVacancy&text=Python+junior&from=suggest_post'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    'accept': '*/*'
}
HOST = 'https://hh.ru'
FILE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.join(FILE, "jobs.csv")

def get_html(url, params=None):
    r = requests.get( url, headers=HEADERS, params=params)
    return r

def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    data_page = None 
    pagination = soup.find_all('span', class_="pager-item-not-in-short-range")
    for i in pagination:
        data_page = i.find('a', class_='bloko-button HH-Pager-Control').get('data-page')
    if data_page == None:
        pagination = soup.find_all('a', class_='bloko-button HH-Pager-Control')
        data_page = len(pagination) + 1
    if data_page:
        return int(data_page)
    else:
        return 0

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_="vacancy-serp-item")
    jobs=[]
    for item in items:
        price = item.find('div', class_="vacancy-serp-item__sidebar").get_text(strip=True)
        if price == '':
            price = "Уточнять"
        try:
            compani = HOST + item.find("a", class_="bloko-link_secondary").get('href')
        except:
            compani = ''
        jobs.append({
            'title': item.find("div", class_='vacancy-serp-item__info').get_text(strip=True),
            'compani': compani, 
            'price': price.replace("\xa0", '')
        })
    return jobs

def save_file(items, path):
    with open(path, 'w', newline="") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([
            "Профессия",
            "Компания",
            "Зарплата"
        ])
        for item in items:
            writer.writerow([item['title'], item['compani'], item['price']])

def parse():
    html = get_html(URL)
    if html.status_code == 200:
        jobs = []
        pages_count = get_pages_count(html.text)
        for page in range(0, pages_count):
            print(f'Парсинг страницы {page + 1} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            jobs.extend(get_content(html.text))
        print(f'Получено {len(jobs)} вакансий на работу')
        save_file(jobs, FILE)
    else:
        print('Error')

parse()