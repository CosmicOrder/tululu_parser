import requests
from bs4 import BeautifulSoup


def get_author_and_title(url):
    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')

    title_book = soup.find('title').text.split(' - ')[0]
    author = soup.find('div', id="content").find('h1').find('a').text
    print('Заголовок:', title_book)
    print('Автор:', author)


if __name__ == '__main__':
    url = "https://tululu.org/b15467/"

    get_author_and_title(url)
