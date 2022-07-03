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
    book_table = soup.find('div', id='content').find_all('table')[0]
    path = book_table.find('a')['href']

    page = None
    book_url = urljoin(f'https://tululu.org/l55/{page}', path)
    print(book_url)


if __name__ == '__main__':
    url = 'https://tululu.org/l55/'

    parse_book_url(url)

