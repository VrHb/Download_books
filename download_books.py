import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath
import requests
from requests import Response


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


def get_title_params_from_book(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("body").find("table")
    title = table.find("h1")
    splited_title = title.text.split("::")
    book_title = splited_title[0].strip().lstrip("\xa0")
    return book_title


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise requests.HTTPError


def main() -> None:
    book_ids = list(range(1, 11))
    for book_id in book_ids:
        url = f"https://tululu.org/txt.php?id={book_id}"
        title = get_title_params_from_book(f"https://tululu.org/b{book_id}/")
        try:
            download_txt(url, f"{book_id}.{title}.txt")
        except:
            continue
if __name__ == "__main__":
    main()

