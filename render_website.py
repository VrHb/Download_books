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


def render_site(books_pages):
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    for page_index, books_page in enumerate(books_pages):
        path_file = os.path.join("pages", f"index{page_index}.html")
        rendered_page = template.render(
            books=books_page 
        )
        with open(path_file, "w", encoding="utf8") as file:
            file.write(rendered_page)


def main():
    books = get_bookinfo_from_json("books_info.json")
    books = list(chunked(books, 2))
    books_pages = list(chunked(books, 10))
    os.makedirs("pages", exist_ok=True)
    render_site(books_pages)
    

if __name__ == "__main__":
    main()
    server = Server()
    server.watch("template.html", main)
    server.serve(root=".")
