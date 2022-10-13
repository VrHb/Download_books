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


FUNCTION_MAP = {
    "skip_img": download_image,
    "skip_txt": download_txt
}

class Argument(NamedTuple):
    start_page: int
    end_page: int
    skip_imgs: bool
    skip_txt: bool
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
        "--skip_imgs",
        action="store_true",
        help="Без обложек книг"
    )
    parser.add_argument(
        "--skip_txt",
        action="store_true",
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
        skip_imgs=args.skip_imgs,
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


def get_book_description(url: str, book: str, arguments: Argument) -> Book:
    book_url = urljoin(url, book.select_one("a")["href"])
    book_id = urlsplit(book_url).path.strip("/b")
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)
    book_page = response.text
    parsed_page = parse_book_page(book_page)
    book_path = os.path.join(
        arguments.dest_folder,
        "books",
        f"{parsed_page.title}.txt"
    )
    book_description = {
        "title": parsed_page.title,
        "author": parsed_page.author,
        "img_src": parsed_page.image,
        "book_path": book_path,
        "comments": parsed_page.comments,
        "genres": parsed_page.genres
    }
    return Book(book_id, book_description, parsed_page)
    

def main() -> None:
    arguments = get_arguments()
    logger.info(arguments.skip_txt)
    page_ids = range(int(arguments.start_page), int(arguments.end_page))
    books_description = []
    for page_id in page_ids:
        try:
            url = f"https://tululu.org/l55/{page_id}/"
            books_on_page = get_books_on_page(url)    
            for book in books_on_page:
                try:
                    book = get_book_description(url, book, arguments)
                    url = "https://tululu.org/txt.php"
                    payload = {"id": f"{book.book_id}"}    
                    books_description.append(book.description)
                    os.makedirs(arguments.dest_folder, exist_ok=True)
                    if arguments.skip_imgs:
                        download_txt(
                            url,
                            payload,
                            f"{book.parsed.title}.txt",
                            os.path.join(arguments.dest_folder, "books") 
                        )
                    if arguments.skip_txt:
                        download_image(
                            book.parsed.image,
                            os.path.join(arguments.dest_folder, "images")
                        )
                    else:
                        download_txt(
                            url,
                            payload,
                            f"{book.parsed.title}.txt",
                            os.path.join(arguments.dest_folder, "books") 
                        )
                        download_image(
                            book.parsed.image,
                            os.path.join(arguments.dest_folder, "images")
                        )
                except requests.HTTPError:
                    logger.error("Книги с таким id нет!")
                    continue
                except requests.ConnectionError:
                    logger.exception("Нет сетевого соединения!")
                    time.sleep(45)
                logger.info("____________________________________")
                logger.info(f"Название книги: {book.parsed.title}")
                logger.info(f"Автор: {book.parsed.author}")
        except requests.HTTPError:
            logger.exception("Такой страницы нет!")
        except requests.ConnectionError:
            logger.exception("Нет соединения с хостом!")
    os.makedirs(arguments.json_path, exist_ok=True)
    json_path = os.path.join(arguments.json_path, "books_info.json")
    with open(json_path, "w") as file_path:
        json.dump(
            books_description,
            file_path,
            indent=4,
            ensure_ascii=False
        )
if __name__ == "__main__":
    main()
      

