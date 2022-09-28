import argparse
import os
from typing import NamedTuple
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
import requests
from requests import Response


class ParsedPage(NamedTuple):
    title: str
    image: str
    genres: list[str]
    author: str


def download_txt(
    url: str, params: dict, filename: str, folder: str = "books/"
    ) -> str:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)
    return filepath


def download_image(url: str, folder: str = "images/") -> None:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filename = urlsplit(url).path.split("/")[-1]
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "wb") as file:
        file.write(response.content)


def download_comments(
    url: str, filename: str, folder: str = "comments/"
    ) -> list[str]:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    comments = soup.find("body").find("table").find_all(class_="texts")
    filepath = os.path.join(folder, filename)
    clear_filepath = sanitize_filepath(filepath)
    with open(clear_filepath, "w") as file:
        for comment in comments:
            file.write(f"{comment.find('span').text}\n")
    return [comment.find("span").text for comment in comments]


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
    return ParsedPage(
        book_title, 
        image_url, 
        [genre.text for genre in genres],
        author
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
        payload = {"id": f"{book_id}"}
        url = f"https://tululu.org/txt.php"
        try:
            book_url = f"https://tululu.org/b{book_id}/"
            response = requests.get(book_url)
            response.raise_for_status()
            book_page = response.text
            parsed_page = parse_book_page(book_page, book_url)
            download_txt(url, payload, f"{book_id}.{parsed_page.title}.txt")
            download_image(parsed_page.image)
            comments = download_comments(book_url, f"{book_id}_comments.txt")
            print(parsed_page.title)
            print(parsed_page.genres)
            print(parsed_page.image)
            print(comments)
        except:
            continue


if __name__ == "__main__":
    main()

