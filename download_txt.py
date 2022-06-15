from urllib.parse import urljoin, urlparse

import requests
import os.path
from pathvalidate import sanitize_filename
from pathlib import Path
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
    return book_title


def get_book_cover(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')

    cover = soup.find('div', class_='bookimage').find('img')['src']
    # cover = urljoin('https://tululu.org', cover)
    return cover


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    filename = sanitize_filename(filename)
    Path(folder).mkdir(exist_ok=True)

    id = int(filename.split('.')[0])

    payload = {"id": id}
    r = requests.get(url, params=payload)
    r.raise_for_status()

    try:
        check_for_redirect(r)
    except HTTPError:
        print(f"Ссылка на скачивание для книги с id{id} не найдена")
    else:
        with open(os.path.join(folder, filename), 'w') as file:
            file.write(r.text)
            return os.path.join(folder, filename)


def download_image(path, folder='images/'):
    """Функция для скачивания текстовых файлов.
    Args:
        path (str): Путь до требуемой картинки.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до картинки обложки.
    """
    Path(folder).mkdir(exist_ok=True)

    image_name = path.split('/')[-1]
    url = urljoin('https://tululu.org', path)

    r = requests.get(url)
    r.raise_for_status()

    with open(os.path.join(folder, image_name), 'wb') as file:
        file.write(r.content)
        return os.path.join(folder, image_name)


if __name__ == '__main__':
    filenames = []
    book_covers = []
    for id in range(1, 11):
        book_url = f"https://tululu.org/b{id}/"
        try:
            book_covers.append(get_book_cover(book_url))
        except HTTPError:
            print(f"Обложка книги с id{id} не найдена")
            continue

        try:
            filenames.append(f"{id}." + get_book_title(book_url) + ".txt")
        except HTTPError:
            print(f"Книга с id{id} не найдена")
            continue

    for filename in filenames:
        download_url = "https://tululu.org/txt.php"
        download_txt(download_url, filename)

    for book_cover in book_covers:
        download_image(book_cover)
