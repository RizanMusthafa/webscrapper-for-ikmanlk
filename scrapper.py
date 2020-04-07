import requests
from bs4 import BeautifulSoup

response = requests.get('https://ikman.lk/en/ads?by_paying_member=0&sort=relevance&buy_now=0&query=bmw&page=1')

scrapper = BeautifulSoup(response.text, 'html.parser')

print(scrapper.find('title').getText())
