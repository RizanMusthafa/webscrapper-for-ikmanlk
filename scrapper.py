from bs4 import BeautifulSoup
import json
import requests
from datetime import datetime, timedelta

APP_BASE_URL = 'https://ikman.lk'

req_url = 'https://ikman.lk/en/ads?by_paying_member=0&sort=relevance&buy_now=0&query=samsung%20s4&page=1'


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


def get_script_for_detail_page(url):
    ad_detail_html = requests.get(url).text
    print('fetching ad details...')
    ad_detail_scrapper = BeautifulSoup(ad_detail_html, 'html5lib')
    return ad_detail_scrapper.findAll('script')


def get_image_url_from_meta_data(meta):
    return list(map(lambda d: d['src'], meta))


def extract_add_detail_data(url):

    scripts = get_script_for_detail_page(url)

    while len(scripts) != 11:
        print('reloading for the page propper render...')
        scripts = get_script_for_detail_page(url)

    print(f'scripts loaded...')

    data_script = scripts[1].getText()[28:-1]

    data = json.loads(data_script)['adDetail']['data']['ad']

    contact = data['contactCard']['phoneNumbers']

    if len(contact) > 0:
        contact = contact[0]['number']
    else:
        contact = None

    return {
        "full_description": data['description'],
        "image_urls": get_image_url_from_meta_data(data['images']['meta']),
        "price": data['money']['amount'],
        "contact": contact
    }


def extract_data_from_ad_list(item):
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

    print(f'<======= {len(ad_list)} ads found =======>')
    list_detail_dict = list(map(extract_data_from_ad_list, ad_list))

    print('\n\n<====== DATA ======>\n')
    print(list_detail_dict)
    with open('output.json', 'w') as output:
        json.dump(list_detail_dict, output)
    print('\n\n<====== END ======>\n')


get_ads_data(req_url)
