import argparse
import os.path
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests import HTTPError


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'start_id',
        help='initial id of downloaded books',
        type=int,
    )
    parser.add_argument(
        'end_id',
        help='ending id of downloaded books',
        type=int,
    )

    return parser


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_title_and_cover(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('title').text.split(' - ')[0]
    book_cover = soup.find('div', class_='bookimage').find('img')['src']
    return book_title, book_cover


def download_txt(url, filename, book_id, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    payload = {"id": book_id}

    response = requests.get(url, params=payload)
    response.raise_for_status()
    check_for_redirect(response)

    with open(os.path.join(folder, filename), 'w',
              encoding='utf-8') as file:
        file.write(response.text)
        return os.path.join(folder, filename)


def download_image(path, folder='images/'):
    Path(folder).mkdir(exist_ok=True)
    image_name = path.split('/')[-1]
    url = urljoin('https://tululu.org', path)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(os.path.join(folder, image_name), 'wb') as \
            file:
        file.write(response.content)
        return os.path.join(folder, image_name)


if __name__ == '__main__':
    download_url = "https://tululu.org/txt.php"
    book_titles_and_covers = []
    parser = create_parser()
    args = parser.parse_args()
    connection_error = False
    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        try:
            book_titles_and_covers.append(get_book_title_and_cover(book_url))
        except HTTPError:
            print(f"Страница или обложка книги b{book_id} не найдена")
            book_titles_and_covers.append(('', ''))
        except ConnectionError:
            print(f"Сбой при подключение к интернету")
            if connection_error:
                time.sleep(2)
            connection_error = True

    for book_id, filename_book_cover in enumerate(book_titles_and_covers,
                                                  args.start_id):
        filename, book_cover = filename_book_cover
        filename = sanitize_filename(filename)
        filename = f"{book_id}.{filename}.txt"
        try:
            download_txt(download_url, filename, book_id)
            download_image(book_cover)
        except HTTPError:
            print(f"Ссылка для скачивания книги с id{book_id} не найдена")
