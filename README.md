# Скачиваем книги с сайта tutlulu.org

Программа позволяет автоматизировать загрузку книг с сайта [tululu.org](https://tululu.org/).

## Сайт проекта

Сайт проекта с книгами доступен [тут](https://vrhb.github.io/Download_books/pages/index1.html).

## Запуск

- Скачайте код.
- Активируйте виртуальное окружение командой:
```
python -m venv <название виртуального окружения>
```
- Установите зависимости: 
```
pip install -r requirements.txt
```
- Запуститите программу:
```
python download_book.py --start_id <id книги с которой начать скачивать> --end_id <id конечной книги>
```
Пример:
```
python download_book.py --start_id 10 --end_id 40
```

### Скачивание книг по жанру

- Запустите программу:
```
python parse_tululu_category.py
```

- Доступные аргументы:
    * dest_folder - путь к директории с результатами парсинга

    пример:
    ```
    python parse_tululu_category.py --dest_category tululu_books/
    ```

    * skip_image - без картинок

    пример:

    ```
    python parse_tululu_category.py --skip_image
    ```

    * skip_txt - не загружать книги

    пример:
    ```
    python parse_tululu_category.py --skip_txt
    ```

    * json_path - путь к JSON с результатами

    пример:
    ```
    python parse_tululu_category.py --json_path /home/user/book_json
    ```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).

