import json
import os.path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
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

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
