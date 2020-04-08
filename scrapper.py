from bs4 import BeautifulSoup
import json
import requests
from datetime import datetime, timedelta

APP_BASE_URL = 'https://ikman.lk'

req_url = 'https://ikman.lk/en/ads?by_paying_member=0&sort=relevance&buy_now=0&query=bmw&page=1'


def get_date_diff(unit, value):
    time_stamp_map = {
        'second': value/(3600 * 24),
        'seconds': value/(3600 * 24),
        'minute': value/(60 * 24),
        'minutes': value/(60 * 24),
        'hour': value/24,
        'hours': value/24,
        'day': value,
        'days': value,
    }
    return datetime.now() - timedelta(days=time_stamp_map[unit])


def extract_add_detail_data(url):
    ad_detail_html = requests.get(url).text
    # print('ad_detail_html', ad_detail_html)
    ad_detail_scrapper = BeautifulSoup(ad_detail_html, 'html.parser')
    # item_body = ad_detail_scrapper.find(class_='item-body')
    description = ad_detail_scrapper.find(class_='item-description')
    price = ad_detail_scrapper.find(class_='amount')
    contact = ad_detail_scrapper.find('span', class_='h3')

    if description is not None:
        description = description.getText()
    # else:
    #     Html_file = open("data.html", "w")
    #     Html_file.write(ad_detail_html)
    #     Html_file.close()

    if price is not None:
        price = price.getText()

    if contact is not None:
        contact = contact.getText()

    return {
        "full_description": description,
        "image_urls": [],
        "price": price,
        "contact": contact
    }


def extract_data_from_ad_list(item):
    # anchor_tag = item.find('a')
    ad_detail_url = f'{APP_BASE_URL}/en/ad/{item["slug"]}'
    detail_data = extract_add_detail_data(ad_detail_url)

    time_stamp = item['timeStamp']
    time_stamp_list = time_stamp.split(' ')
    date = get_date_diff(time_stamp_list[1], int(time_stamp_list[0]))

    return {
        "title": item['title'],
        "date": date.date().strftime('%Y-%m-%d'),
        "short_description": item['description'],
        "category": item['category'],
        "url": ad_detail_url,
        "details": detail_data
    }


def get_ads_data(url):
    ad_list_html = requests.get(url).text
    ad_list_scrapper = BeautifulSoup(ad_list_html, 'html5lib')
    script = ad_list_scrapper.findAll('script')[1].getText()
    ad_list_data = json.loads(script[28:-1])['serp']['ads']['data']
    ad_list = ad_list_data['ads'] + ad_list_data['topAds']
    list_detail_dict = list(map(extract_data_from_ad_list, ad_list))
    # with open('data.json', 'w') as output_file:
    #     json.dump(list_detail_dict, output_file)
    print(list_detail_dict)


get_ads_data(req_url)
