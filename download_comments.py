import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_title(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')
    book_title = soup.find('title').text.split(' - ')[0]
    print(book_title, end='\n\n')


def download_comments(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')

    for i in soup.find_all('div', class_='texts'):
        print(i.find('span').text, end='\n\n')


if __name__ == '__main__':
    for i in range(1, 11):
        book_url = f"https://tululu.org/b{i}/"
        try:
            get_book_title(book_url)
            download_comments(book_url)
        except HTTPError:
            # print(f"Книга с id{i} не найдена")
            continue
