import argparse
import os
import time
from typing import NamedTuple
import json
from urllib.parse import urljoin, urlsplit
from bs4.element import ResultSet

import requests
from bs4 import BeautifulSoup
from loguru import logger

from download_books import ParsedPage, download_txt, download_image, parse_book_page, \
    check_for_redirect


class Argument(NamedTuple):
    start_page: int
    end_page: int
    skip_img: str
    skip_txt: str
    dest_folder: str
    json_path: str

class Book(NamedTuple):
    book_id: str
    description: dict
    parsed: ParsedPage


def get_arguments() -> Argument:
    parser = argparse.ArgumentParser(
        description="Постранично загружаем книги с сайта tululu.org"
    )
    parser.add_argument(
        "--start_page",
        default=1,
        help="Стартовая страница с книгами"
    )
    parser.add_argument(
        "--skip_img",
        action="store_false",
        help="Без обложек книг"
    )
    parser.add_argument(
        "--skip_txt",
        action="store_false",
        help="Не скачивать книги"
    )
    parser.add_argument(
        "--end_page",
        default=701,
        help="Конечная страница с книгами"
    )
    parser.add_argument(
        "--dest_folder",
        default=".",
        help="Директория для сохранения"
    )
    parser.add_argument(
        "--json_path",
        default=".",
        help="Путь для сохранения json с информацией по книгам"
    )
    args = parser.parse_args()
    return Argument(
        start_page=args.start_page,
        end_page=args.end_page,
        skip_img=args.skip_img,
        skip_txt=args.skip_txt,
        dest_folder=args.dest_folder,
        json_path=args.json_path
    )


def get_books_on_page(url: str) -> ResultSet:
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, "lxml")
    selector = "body table.tabs div.bookimage"
    books_on_page = soup.select(selector)
    return books_on_page


def get_book_description(book: str, arguments: Argument) -> Book:
    book_url = urljoin("https://tululu.org", book.select_one("a")["href"])
    book_id = urlsplit(book_url).path.strip("/b")
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    book_page = response.text
    parsed_page = parse_book_page(book_page)
    book_description = {
        "title": parsed_page.title,
        "author": parsed_page.author,
        "img_src": parsed_page.image,
        "book_path": f"{arguments.dest_folder}/books/{parsed_page.title}.txt",
        "comments": parsed_page.comments,
        "genres": parsed_page.genres
    }
    return Book(book_id, book_description, parsed_page)


def main() -> None:
    arguments = get_arguments()
    page_ids = range(int(arguments.start_page), int(arguments.end_page))
    books_description = []
    for page_id in page_ids:
        try:
            url = f"https://tululu.org/l55/{page_id}/"
            books_on_page = get_books_on_page(url)
            for book in books_on_page:
                    book = get_book_description(book, arguments)
                    url = f"https://tululu.org/txt.php"
                    payload = {"id": f"{book.book_id}"}    
                    books_description.append(book.description)
                    os.makedirs(arguments.dest_folder, exist_ok=True)
                    if arguments.skip_img:
                        download_image(
                            book.parsed.image,
                            os.path.join(arguments.dest_folder, "images")
                        )
                    if arguments.skip_txt:
                        download_txt(
                            url,
                            payload,
                            f"{book.parsed.title}.txt",
                            os.path.join(arguments.dest_folder, "books") 
                        )
                    logger.info(f"Название книги: {book.parsed.title}")
                    logger.info(f"Автор: {book.parsed.author}")
        except requests.HTTPError:
            logger.exception("Книги с таким id нет!")
            continue
        except requests.ConnectionError:
            logger.exception("Нет соединения!")
            time.sleep(15)
    
    json_books_description = json.dumps(
        books_description,
        indent=4,
        ensure_ascii=False
    )
    os.makedirs(arguments.json_path, exist_ok=True)
    with open(f"{arguments.json_path}/books_info.json", "w") as file:
        file.write(json_books_description)


if __name__ == "__main__":
    main()

