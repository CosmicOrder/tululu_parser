import requests
from bs4 import BeautifulSoup
from requests import HTTPError


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

    genres = []
    for genre in current_genres:
        genres.append(genre.text)

    comments = []
    for comment in current_comments:
        comments.append(comment.find('span').text)

    book_page_specs = {
        "title": title,
        "author": author,
        "cover_path": cover_path,
        "genres": genres,
        "comments": comments,
    }
    return book_page_specs


if __name__ == '__main__':
    for i in range(1, 11):
        book_url = f"https://tululu.org/b{i}/"
        try:
            parse_book_page(book_url)
        except HTTPError:
            print(f"Книга с id{i} не найдена")
            continue
