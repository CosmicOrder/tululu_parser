from itertools import count
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def parse_book_url(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_cards = soup.find('div', id='content').find_all('table')

    for book_card in book_cards:
        path = book_card.find('a')['href']
        book_url = urljoin(url, path)
        print(book_url)


if __name__ == '__main__':
    for page in count(1):
        url = f'https://tululu.org/l55/{page}'
        parse_book_url(url)
        if page >= 10:
            break
