import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler, SimpleHTTPRequestHandler

from more_itertools import chunked
from loguru import logger
from livereload import Server, shell
from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_bookinfo_from_json(json_file: str) -> dict:
    with open(json_file, "r") as file:
        book_description = json.load(file)
    return book_description


def render_pages(books_pages):
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    for page_num, books_on_page in enumerate(books_pages, 1):
        path_file = os.path.join("pages", f"index{page_num}.html")
        pages_range = range(1, len(books_pages) + 1)
        rendered_page = template.render(
            books=books_on_page,
            pages=pages_range,
            page_num=page_num
        )
        with open(path_file, "w", encoding="utf8") as file:
            file.write(rendered_page)


def main():
    books = get_bookinfo_from_json("books_info.json")
    num_columns = 2
    column_length = 10
    books_columns = list(chunked(books, num_columns))
    books_pages = list(chunked(books_columns, column_length))
    os.makedirs("pages", exist_ok=True)
    render_pages(books_pages)
    

if __name__ == "__main__":
    main()
    server = Server()
    server.watch("template.html", main)
    server.serve(root=".")
