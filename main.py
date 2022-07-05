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


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_page',
        default=1,
        help='initial page number of downloaded books',
        type=int,
    )
    parser.add_argument(
        '--end_page',
        default=702,
        help='ending page number of downloaded books',
        type=int,
    )
    parser.add_argument(
        '--dest_folder',
        default='parsing_results/',
        help='path to parsing results',
    )
    parser.add_argument(
        '--skip_imgs',
        help='do not download covers',
        action='store_true',
    )
    parser.add_argument(
        '--skip_txt',
        help='do not download books',
        action='store_true',
    )
    parser.add_argument(
        '--json_path',
        default='.',
        help='path to json file with results',
    )
    return parser


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def parse_book_page(html):
    soup = BeautifulSoup(html, 'lxml')

    title_selector = 'title'
    title = soup.select_one(title_selector).text.split(' - ')[0]

    author_selector = '#content h1 a'
    author = soup.select_one(author_selector).text

    cover_selector = '.bookimage img'
    cover_path = soup.select_one(cover_selector)['src']

    genres_selector = 'span.d_book a'
    current_genres = soup.select(genres_selector)

    comments_selector = '.texts .black'
    current_comments = soup.select(comments_selector)

    genres = [genre.text for genre in current_genres]
    comments = [comment.text for comment in current_comments]

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
        "img_src": book.get('img_src'),
        "book_path": book.get('book_path'),
        "comments": book['comments'],
        "genres": book['genres'],
    }


def get_books_url(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    selector = '#content .d_book'
    book_cards = soup.select(selector)

    books_url = []
    for book_card in book_cards:
        path = book_card.select_one('a')['href']
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
    parser = create_parser()
    args = parser.parse_args()
    download_url = "https://tululu.org/txt.php"
    book_urls = []
    books_json = []
    for page in count(args.start_page):
        url = f'https://tululu.org/l55/{page}'
        book_urls += get_books_url(url)
        if page >= args.end_page - 1:
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

            if not args.skip_txt:
                book_page_specs['book_path'] = \
                    download_txt(download_url,
                                 filename,
                                 book_id,
                                 folder=args.dest_folder)

            if not args.skip_imgs:
                book_page_specs['img_src'] = \
                    download_image(
                        cover_path,
                        book_id,
                        folder=args.dest_folder)

            books_json.append(serialize_book(book_page_specs))
        except HTTPError:
            print(f"Страница книги или ссылка на её скачивание "
                  f"b{book_id} не найдена")
        except ConnectionError:
            print(f"Сбой при подключение к интернету")
            time.sleep(2)

    json_path = os.path.join(args.dest_folder, 'books.json')
    with open(json_path, 'w', encoding='utf8') as file:
        json.dump(books_json, file, ensure_ascii=False)
