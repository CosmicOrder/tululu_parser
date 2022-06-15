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
    response = requests.get(url)
    response.raise_for_status()

    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book_title = soup.find('title').text.split(' - ')[0]
    return book_title


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
    response = requests.get(url, params=payload)
    response.raise_for_status()

    try:
        check_for_redirect(response)
    except HTTPError:
        print(f"Ссылка на скачивание для книги с id{id} не найдена")
    else:
        with open(os.path.join(folder, filename), 'w') as file:
            file.write(response.text)
            return os.path.join(folder, filename)


if __name__ == '__main__':
    filenames = []
    for id in range(1, 11):
        book_url = f"https://tululu.org/b{id}/"
        try:
            filenames.append(f"{id}." + get_book_title(book_url) + ".txt")
        except HTTPError:
            print(f"Книга с id{id} не найдена")
            continue

    for filename in filenames:
        download_url = "https://tululu.org/txt.php"
        download_txt(download_url, filename)
