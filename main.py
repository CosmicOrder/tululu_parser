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


def get_book_title(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('title').text.split(' - ')[0]
    return book_title


def get_book_cover(url):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    cover = soup.find('div', class_='bookimage').find('img')['src']
    return cover


def download_txt(url, filename, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    filename = sanitize_filename(filename)
    book_id = int(filename.split('.')[0])

    payload = {"id": book_id}

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
        check_for_redirect(response)
    except HTTPError:
        print(f"Ссылка на скачивание для книги с id{book_id} не найдена")
    else:
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
    filenames = []
    book_covers = []
    parser = create_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        try:
            filenames.append(f"{book_id}." + get_book_title(book_url) + ".txt")
        except HTTPError:
            print(f"Странице книги b{book_id} не найдена")
            continue
        try:
            book_covers.append(get_book_cover(book_url))
        except HTTPError:
            print(f"Обложка книги с b{book_id} не найдена")
            continue

    for filename in filenames:
        download_txt(download_url, filename)

    for book_cover in book_covers:
        download_image(book_cover)
