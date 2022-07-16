import json
import os.path
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('template.html')

    source_path = os.path.join('parsing_results/', 'books.json')
    with open(source_path, 'r', encoding='utf-8') as file:
        books_specs = json.load(file)

    rendered_page = template.render(books=books_specs)

    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve()
