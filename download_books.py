import argparse
import os
import time
from typing import NamedTuple
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from loguru import logger
from pathvalidate import sanitize_filepath
import requests
from requests import Response


logger.debug("Console log")

class ParsedPage(NamedTuple):
    title: str
    image: str
    genres: list[str]
    author: str
    comments: list[str]


def download_txt(
    url: str, params: dict, filename: str, folder: str = "books/"
    ) -> None:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)


def download_image(image_path: str, folder: str = "images/") -> None:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(urljoin("https://tululu.org", image_path))
    response.raise_for_status()
    filename = urlsplit(image_path).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)


def download_comments(
    comments: list[str], filename: str, folder: str = "comments/"
    ) -> None:
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "w") as file:
        for comment in comments:
            file.write(f"{comment}\n")


def parse_book_page(page: str, book_url: str | None = None) -> ParsedPage:
    soup = BeautifulSoup(page, "lxml")
    title = soup.find("body").find("table").find("h1")
    splited_title = title.text.split("::")
    book_title, author = [
        text.strip().lstrip("\xa0") for text in splited_title
    ]
    image = soup.find(class_="bookimage").find("img")["src"]
    image_url = urljoin(book_url, image) 
    genres = soup.find("body").find(class_="ow_px_td") \
        .find("span", class_="d_book").find_all("a")
    comments = soup.find("body").find("table").find_all(class_="texts")
    return ParsedPage(
        book_title, 
        image_url, 
        [genre.text for genre in genres],
        author,
        [comment.find("span").text for comment in comments]
    )


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise requests.HTTPError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Программа загружает книги с сайта tululu.org"
    )
    parser.add_argument(
        "--start_id",
        default=1,
        help="Стартовый идентификатор книги"
    )
    parser.add_argument(
        "--end_id",
        default=10,
        help="Конечный идентификатор книги"
    )
    args = parser.parse_args()
    book_ids = range(int(args.start_id), int(args.end_id) + 1)
    for book_id in book_ids:
        try:
            url = f"https://tululu.org/txt.php"
            book_url = f"https://tululu.org/b{book_id}/"
            payload = {"id": f"{book_id}"}
            response = requests.get(book_url)
            check_for_redirect(response)
            response.raise_for_status()
            book_page = response.text
            parsed_page = parse_book_page(book_page, book_url)
            download_txt(url, payload, f"{book_id}.{parsed_page.title}.txt")
            download_image(parsed_page.image)
            download_comments(parsed_page.comments, f"{book_id}_comments.txt")
            logger.info(f"Название книги: {parsed_page.title}")
            logger.info(f"Автор: {parsed_page.author}")
            logger.info(f"Жанр: {parsed_page.genres}")
        except requests.HTTPError:
            logger.exception("Книги с таким id нет!")
            continue
        except requests.ConnectionError:
            logger.exception("Нет соединения!")
            time.sleep(15)

if __name__ == "__main__":
    main()

