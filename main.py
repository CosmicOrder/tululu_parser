import os.path
from pathlib import Path

import requests
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def download_books(url):
    for i in range(1, 11):
        payload = {"id": i}

        response = requests.get(url, params=payload)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except HTTPError:
            print(f"Книга с id{i} не найдена")
            i += 1
        with open(os.path.join("books", f"id{i}.txt"), "w") as file:
            file.write(response.text)


if __name__ == '__main__':
    url = "https://tululu.org/txt.php"
    Path("books").mkdir(exist_ok=True)

    download_books(url)
