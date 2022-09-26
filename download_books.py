import os

from bs4 import BeautifulSoup
from pathvalidate import is_valid_filename, sanitize_filename
import requests
from requests import Response


def download_txt(url: str, filename: str, folder: str = "books/") -> str:
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    filepath = os.path.join(folder, sanitize_filename(f"{filename}.txt"))
    with open(filepath, "wb") as file:
        file.write(response.content)
    return filepath


def parse_page(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    table = soup.find("body").find("table")
    title = table.find("h1")
    splited_title = title.text.split("::")
    author = splited_title[1].strip().rstrip("\xa0")
    book_title = splited_title[0].strip().lstrip("\xa0")
    return f"Заголовок: {book_title}\nАвтор: {author}"


def check_for_redirect(response: Response) -> None:
    if response.history:
        raise requests.HTTPError


def main() -> None:
    os.makedirs("books", exist_ok=True)
    url = "http://tululu.org/txt.php?id=1"
    filepath = download_txt(url, "Али\\би", "txt")
    print(filepath)
    """
    book_ids = list(range(1, 11))
    parsed_page = parse_page("https://tululu.org/b1/")
    print(parsed_page)
    for book_id in book_ids:
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()
        try: 
            check_for_redirect(response)
            filename = f"books/id{book_id}.txt"
            with open(filename, "wb") as file:
                file.write(response.content)
        except:
            continue
    """
if __name__ == "__main__":
    main()

