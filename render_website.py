import json
from http.server import HTTPServer, SimpleHTTPRequestHandler, SimpleHTTPRequestHandler


from loguru import logger
from jinja2 import Environment, FileSystemLoader, select_autoescape



def get_bookinfo_from_json(json_file: str) -> dict[str]:
    with open(json_file, "r") as file:
        book_description = json.load(file)
    return book_description


def main():
    books = get_bookinfo_from_json("books_info.json")

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
       books=books 
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()
