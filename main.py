import argparse
import json
import os.path
import time
from itertools import count
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')

    title = soup.find('title').text.split(' - ')[0]
    author = soup.find('div', id="content").find('h1').find('a').text
    cover_path = soup.find('div', class_='bookimage').find('img')['src']
    current_genres = soup.find('span', class_='d_book').find_all('a')
    current_comments = soup.find_all('div', class_='texts')

    genres = [genre.text for genre in current_genres]
    comments = [comment.find('span').text for comment in current_comments]

    book_page_specs = {
        "title": title,
        "author": author,
        "cover_path": cover_path,
        "genres": genres,
        "comments": comments,
    }
    return book_page_specs


def serialize_book(book):
    return {
        "title": book['title'],
        "author": book['author'],
        "img_src": book['img_src'],
        "book_path": book['book_path'],
        "comments": book['comments'],
        "genres": book['genres'],
    }


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

    return books_url


def download_txt(url, filename, book_id, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    payload = {"id": book_id}

    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    path = os.path.join(folder, filename)
    with open(path, 'w', encoding='utf-8') as file:
        file.write(response.text)
        return path


def download_image(path, book_id, folder='images/'):
    Path(folder).mkdir(exist_ok=True)
    image_name = path.split('/')[-1]
    url = urljoin(f'https://tululu.org/b{book_id}/', path)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    path = os.path.join(folder, image_name)
    with open(path, 'wb') as file:
        file.write(response.content)
        return path


if __name__ == '__main__':
    download_url = "https://tululu.org/txt.php"
    book_urls = []
    books_json = []
    for page in count(1):
        url = f'https://tululu.org/l55/{page}'
        book_urls += get_books_url(url)
        if page >= 4:
            break

    for book_url in book_urls:
        book_id = urlsplit(book_url).path.replace('/', '').replace('b', '')
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book_page_html = response.text

            book_page_specs = parse_book_page(book_page_html)
            filename = book_page_specs['title']
            cover_path = book_page_specs['cover_path']

            filename = sanitize_filename(filename)
            filename = f"{filename}.txt"

            book_page_specs['book_path'] = download_txt(download_url, filename, book_id)
            book_page_specs['img_src'] = download_image(cover_path, book_id)

            books_json.append(serialize_book(book_page_specs))
        except HTTPError:
            print(f"Страница книги или ссылка на её скачивание "
                  f"b{book_id} не найдена")
        except ConnectionError:
            print(f"Сбой при подключение к интернету")
            time.sleep(2)

    with open('books.json', 'w', encoding='utf8') as file:
        json.dump(books_json, file, ensure_ascii=False)
