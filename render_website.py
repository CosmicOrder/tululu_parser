import json
import math
import os.path
from pathlib import Path

import more_itertools
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

    books_specs = list(more_itertools.chunked(books_specs, 2))
    count_of_book_pairs = len(books_specs)

    for i, j in enumerate(range(0, count_of_book_pairs, 5), 1):
        folder = 'pages'
        filename = f'index{i}.html'
        Path(folder).mkdir(exist_ok=True)
        rendered_page = template.render(books=books_specs[j:j+5],
                                        current_page=i,
                                        page_count=math.ceil(
                                            count_of_book_pairs / 5))

        path = os.path.join(folder, filename)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve()
