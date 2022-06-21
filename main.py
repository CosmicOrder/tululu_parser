import argparse
import os.path
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
    book_titles = []
    book_covers = []
    parser = create_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        try:
            book_titles.append(f"{book_id}." +
                               get_book_title_and_cover(book_url)[0] + ".txt")
        except HTTPError:
            print(f"Странице книги b{book_id} не найдена")
            continue
        try:
            book_covers.append(get_book_title_and_cover(book_url)[1])
        except HTTPError:
            print(f"Обложка книги с b{book_id} не найдена")
            continue

    for filename in book_titles:
        book_id = int(filename.split('.')[0])
        try:
            filename = sanitize_filename(filename)
            download_txt(download_url, filename, book_id)
        except HTTPError:
            print(f"Ссылка на скачивание для книги с "
                  f"id{book_id} не найдена")

    for book_cover in book_covers:
        download_image(book_cover)
