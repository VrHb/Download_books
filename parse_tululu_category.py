import argparse
import os
import time
import json
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from loguru import logger

from download_books import download_txt, download_image, parse_book_page, \
    check_for_redirect


def main() -> None:
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

    page_ids = range(int(args.start_page), int(args.end_page))
    books_description = []
    for page_id in page_ids:
        url = f"https://tululu.org/l55/{page_id}/"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        selector = "body table.tabs div.bookimage"
        books_on_page = soup.select(selector)
        for book in books_on_page:
            try:
                url = f"https://tululu.org/txt.php"
                book_url = urljoin("https://tululu.org", book.select_one("a")["href"])
                book_id = urlsplit(book_url).path.strip("/b")
                payload = {"id": f"{book_id}"}    
                response = requests.get(book_url)
                response.raise_for_status()
                check_for_redirect(response)
                book_page = response.text
                parsed_page = parse_book_page(book_page)
                book_description = {
                    "title": parsed_page.title,
                    "author": parsed_page.author,
                    "img_src": parsed_page.image,
                    "book_path": f"{args.dest_folder}/books/{parsed_page.title}.txt",
                    "comments": parsed_page.comments,
                    "genres": parsed_page.genres
                }
                books_description.append(book_description)
                os.makedirs(args.dest_folder, exist_ok=True)
                if args.skip_img:
                    download_image(
                        parsed_page.image,
                        os.path.join(args.dest_folder, "images")
                    )
                if args.skip_txt:
                    download_txt(
                        url,
                        payload,
                        f"{parsed_page.title}.txt",
                        os.path.join(args.dest_folder, "books") 
                    )
                logger.info(f"Название книги: {parsed_page.title}")
                logger.info(f"Автор: {parsed_page.author}")
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
    os.makedirs(args.json_path, exist_ok=True)
    with open(f"{args.json_path}/books_info.json", "w") as file:
        file.write(json_books_description)


if __name__ == "__main__":
    main()

