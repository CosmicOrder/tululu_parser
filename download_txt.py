from urllib.parse import urljoin

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


def get_title_and_cover(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')

    book_title = soup.find('title').text.split(' - ')[0]
    cover = soup.find('div', class_='bookimage').find('img')['src']
    cover = urljoin('https://tululu.org', cover)
    print('Заголовок:', book_title)
    print('Автор:', cover)


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


if __name__ == '__main__':
    filenames = []
    for id in range(1, 11):
        book_url = f"https://tululu.org/b{id}/"
        try:
            get_title_and_cover(book_url)
        except HTTPError:
            print(f"Книга с id{id} не найдена")

        # try:
        #     filenames.append(f"{id}." + get_book_title(book_url) + ".txt")
        # except HTTPError:
        #     print(f"Книга с id{id} не найдена")
        #     continue

    # for filename in filenames:
    #     download_url = "https://tululu.org/txt.php"
    #     download_txt(download_url, filename)


