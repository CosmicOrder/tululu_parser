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


def parse_book_page(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')

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
    return print(book_page_specs)


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
    parser = create_parser()
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        book_url = f"https://tululu.org/b{book_id}/"
        try:
            filename, book_cover = get_book_title_and_cover(book_url)
            filename = sanitize_filename(filename)
            filename = f"{book_id}.{filename}.txt"
            download_txt(download_url, filename, book_id)
            download_image(book_cover, book_id)
        except HTTPError:
            print(f"Страница книги или ссылка на её скачивание "
                  f"b{book_id} не найдена")
        except ConnectionError:
            print(f"Сбой при подключение к интернету")
            time.sleep(2)
