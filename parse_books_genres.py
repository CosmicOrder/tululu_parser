import requests
from bs4 import BeautifulSoup
from requests import HTTPError


def check_for_redirect(response):
    if response.history:
        raise HTTPError


def get_book_genres(url):
    r = requests.get(url)
    r.raise_for_status()

    check_for_redirect(r)

    soup = BeautifulSoup(r.text, 'lxml')
    genres = soup.find('span', class_='d_book').find_all('a')
    current_genres = []
    for genre in genres:
        current_genres.append(genre.text)

    current_genres = '; '.join(current_genres)

    print('Жанр:', current_genres)


if __name__ == '__main__':
    for i in range(1, 11):
        book_url = f"https://tululu.org/b{i}/"
        try:
            get_book_genres(book_url)
        except HTTPError:
            print(f"Книга с id{i} не найдена")
            continue
