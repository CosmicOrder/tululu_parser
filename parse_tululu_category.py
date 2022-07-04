from itertools import count
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_books_url(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_cards = soup.find('div', id='content').find_all('table')

    books_url = []
    for book_card in book_cards:
        path = book_card.find('a')['href']
        book_url = urljoin(url, path)
        books_url.append(book_url)

    return print(books_url)


if __name__ == '__main__':
    for page in count(1):
        url = f'https://tululu.org/l55/{page}'
        get_books_url(url)
        if page >= 10:
            break
