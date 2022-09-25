import os

import requests


def main() -> None:
    os.makedirs("books", exist_ok=True)
    book_ids = list(range(1, 11))

    for book_id in book_ids:
        url = f"https://tululu.org/txt.php?id={book_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        filename = f"books/id{book_id}.txt"
        with open(filename, "wb") as file:
            file.write(response.content)

if __name__ == "__main__":
    main()

