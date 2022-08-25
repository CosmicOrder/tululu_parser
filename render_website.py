import json
import os.path
from pathlib import Path

from more_itertools import chunked
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

    books_specs_pages = list(chunked(chunked(books_specs, 2), 5))

    for index, books_specs_page in enumerate(books_specs_pages, 1):
        folder = 'pages'
        filename = f'index{index}.html'
        Path(folder).mkdir(exist_ok=True)
        rendered_page = template.render(books=books_specs_page,
                                        current_page=index,
                                        page_count=len(books_specs_pages))

        path = os.path.join(folder, filename)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve()
