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


def download_txt(url: str, filename: str, folder: str = "books/") -> str:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
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


def download_comments(url: str, filename: str, folder: str = "comments/") -> list[str]:
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
    return comments


def parse_book_page(url: str) -> ParsedPage:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    title = soup.find("body").find("table").find("h1")
    splited_title = title.text.split("::")
    book_title = splited_title[0].strip().lstrip("\xa0")
    author = splited_title[1].strip().lstrip("\xa0")
    image = soup.find(class_="bookimage").find("img")["src"]
    image_url = urljoin("http://tululu.org/", image) 
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
    book_ids = list(range(1, 11))
    for book_id in book_ids:
        url = f"https://tululu.org/txt.php?id={book_id}"
        try:
            book_url = f"https://tululu.org/b{book_id}/"
            title = parse_book_page(book_url).title
            download_txt(url, f"{book_id}.{title}.txt")
            image_url = parse_book_page(book_url).image
            genres = parse_book_page(book_url).genres
            download_image(image_url)
            print(title)
            print(genres)
            print(image_url)
            """
            comments = download_comments(book_url, f"{book_id}_comments.txt")
            for comment in comments:
                print(comment.find("span").text)
            """
        except:
            continue


if __name__ == "__main__":
    main()

