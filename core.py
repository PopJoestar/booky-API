import concurrent.futures
import math
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

FICTION_LATEST = "http://libgen.rs/fiction/recent"
NON_FICTION_BASE_URL = "http://libgen.rs/search.php?"
NON_FICTION_DETAILS_URL = "http://library.lol/main/"
FICTION_BASE_URL = "http://libgen.rs/fiction/?"
FICTION_DETAILS_BASE_URL = "http://library.lol/fiction/"
TIMEOUT = 10
MAX_REQUEST_DETAILS_TRY = 10
MAX_REQUEST_TRY = 20
IMAGE_SOURCE = "https://libgen.is"
MAX_ITEMS_PER_PAGE = 25

NON_FICTION_ITEMS_PER_PAGE = 50

MAX_SHOWING_RESULTS = 10000
VALID_EXTENSION = {'pdf', 'epub', 'zip', 'rar',
                   'azw', 'azw3', 'fb2', 'mobi', 'djvu'}
AVAILABLE_LANGUAGE = {
    'anglais',
    'français',
    'french',
    'english',
    'swedish',
    'spanish',
    'german',
    'italian',
    'dutch',
    'portuguese',
    'lithuanian',
    'slovak',
    'czech',
    'chinese',
    'japanese',
    'bengali',
    'greek',
    'polish',
}


def create_url(base_url, params):
    encoded_params = ''
    if params and params != {}:
        encoded_params = urlencode(params)
    result = base_url + encoded_params
    return result


def get_book_details(session, book_md5, book_type, ua):
    is_fiction = book_type == 'fiction'
    nbr_of_request = 0
    url = FICTION_DETAILS_BASE_URL if is_fiction else NON_FICTION_DETAILS_URL
    url = url + book_md5

    headers = {
        'user-agent': ua.random,
        'Referer': 'http://libgen.rs/',
        'Host': 'library.lol',
    }

    result = {
        book_md5: "",
        'authors': [],
        'type': book_type,
        'publisher': "",
        'isbn': [],
        "series": "",
        'description': "",
        "image": "",
        "download_links": [],
        'year': ''
    }

    try:

        r = session.get(url, headers=headers, timeout=TIMEOUT)

        while r.status_code != 200 and nbr_of_request <= MAX_REQUEST_DETAILS_TRY:
            headers = {
                'user-agent': ua.random,
                'Referer': 'http://libgen.rs/',
                'Host': 'library.lol',
                'Connection': 'keep-alive'
            }
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            nbr_of_request = nbr_of_request + 1

        if nbr_of_request <= MAX_REQUEST_TRY:
            soup = BeautifulSoup(r.text, "lxml")

            details_container = soup.find('td', id="info")

            if details_container:
                image = IMAGE_SOURCE + details_container.img['src']
                details = details_container.find_all('p')

                # get the description if exist
                description_container = details_container.find_all("div")
                if len(description_container) > 3:
                    result['description'] = str(description_container[3])

                else:
                    if description_container[-1].text != "":
                        result['description'] = str(description_container[-1])

                # get Author(s), Publisher, ISBN
                for detail in details:
                    if 'Author(s)' in detail.text:
                        res = detail.text.split(":")
                        result.update({
                            'authors': item.split(',') for item in res[-1].strip().split(";")
                        })
                    elif 'Publisher' in detail.text:
                        res = detail.text.split(":")
                        result['publisher'] = res[1].strip().split(",")[0],

                        if not is_fiction:
                            value = res[-1].strip()
                            result['year'] = value if value != "" and value.isdigit(
                            ) else ''

                    elif 'ISBN' in detail.text:
                        res = detail.text.split(":")
                        value = res[-1].strip().split(",") if res[-1] != "" else []
                        if value:
                            result['isbn'] = res[-1].strip().split(",")

                    elif 'Series' in detail.text:
                        res = detail.text.split(":")
                        result['series'] = res[-1].strip()

                    if is_fiction:
                        if 'Year' in detail.text:
                            res = detail.text.split(":")
                            result['year'] = res[-1].strip()

                # get all available download links
                download_container = soup.find(
                    'div', id="download").find_all('a')

                if download_container:
                    download_links = []
                    for link in download_container:
                        download_links.append(link['href'])

                result.update({
                    'image': image,
                    'download_links': download_links
                })

                return result
            else:
                return None
        else:
            return None
    except Exception:
        return None


def get_non_fiction_books(url_params):
    url = create_url(NON_FICTION_BASE_URL, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(url)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        total_item_container = soup.find(
            "font", {'color': "grey", 'size': 1})
        table = soup.find("table", class_="c")

        if total_item_container:
            total_item = int(
                total_item_container.text.strip().split(" ")[0])
            total_item = total_item if total_item <= MAX_SHOWING_RESULTS else MAX_SHOWING_RESULTS
            if total_item == 0:
                return results
        else:
            return results

        tables = soup.find_all("table", {'rules': 'cols'})

        tables.pop(-1)

        for i, table in enumerate(tables):
            # remove all Mirror tables
            if i % 2 == 0:
                book = {}
                page_language = []
                size_extension = []
                rows = table.find_all("tr")

                page_language = rows[6].find_all("td")
                size_extension = rows[9].find_all("td")
                series = rows[3].find_all('td')[1].text.strip()
                publisher = rows[4].find_all('td')[1].text.strip()
                year = rows[5].find_all('td')[1].text.strip()
                isbns = rows[7].find_all(
                    'td')[1].text.strip().replace(' ', '').split(',')

                size_container = size_extension[1].text.strip().split(
                    ' ')

                book.update({
                    'title': rows[1].b.text.strip(),
                    'md5': rows[1].a['href'].strip().split('=')[-1],
                    'language': page_language[1].text.strip(),
                    'size': size_container[0] + size_container[1],
                    'extension': size_extension[-1].text.strip(),
                    'nbrOfPages': page_language[-1].text.strip(),
                    'source': '',
                    'details': {
                        'authors': rows[2].b.text.strip().split(','),
                        'type': 'non-fiction',
                        'publisher': publisher,
                        'isbn': isbns,
                        "series": series,
                        'description': "",
                        "image": IMAGE_SOURCE + rows[1].img['src'].strip(),
                        "download_links": [],
                        'year': year
                    }
                })
                books.append(book)

        results.update({
            'total_item': total_item,
            'total_pages': math.ceil(total_item / NON_FICTION_ITEMS_PER_PAGE),
            'items': books
        })
        return results

    except Exception as e:
        raise Exception(e.__str__)


def get_fiction_books(url_params):
    url = create_url(FICTION_BASE_URL, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []

    try:
        r = get_html_container(url)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        non_break_space = u'\xa0'

        table = soup.find("table", class_="catalog")
        total_items_container = soup.find("div", style="float:left")

        if total_items_container:
            total_items = int(total_items_container.text.strip().split(" ")[
                0].replace(non_break_space, ''))
            results.update({
                'total_item': total_items,
                'total_pages': math.ceil(total_items / MAX_ITEMS_PER_PAGE)
            })
        else:
            return results

        if table:
            rows = table.find_all("tr")
            rows.pop(0)

            for row in rows:
                book = {}
                data = row.find_all("td")

                file_info = data[4].text.strip().split("/")
                extension = file_info[0].strip().lower()
                language = data[3].text.strip()

                if extension.lower() in VALID_EXTENSION and language.lower() in AVAILABLE_LANGUAGE:
                    md5 = data[5].ul.li.a['href'].strip().split("/")[-1]
                    book.update({
                        'title': data[2].text.strip(),
                        'language': language,
                        'size': file_info[-1].strip().replace(non_break_space, ''),
                        'extension': extension,
                        'md5': md5,
                        'nbrOfPages': '',
                        'source': 'recent' if url == FICTION_LATEST else '',
                        'image': '',
                        'details':
                            {'type': 'fiction'}
                    })
                    books.append(book)

            results['items'] = fetch_books_details(books)

        return results

    except Exception as e:
        raise Exception(e.__str__)


def fetch_books_details(books: list):
    ua = UserAgent()
    book_details = []
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        with requests.session() as session:
            temp = {executor.submit(
                get_book_details, session, book['md5'], book['details']['type'], ua): book for book in books}
            for future in concurrent.futures.as_completed(temp):
                try:
                    data = future.result(timeout=TIMEOUT)
                except Exception:
                    pass
                else:
                    if data:
                        book_details.append(data)

     # map detail to book
    for book in books:
        for detail in book_details:
            if book["md5"] in detail:
                detail.pop(book['md5'])
                book['image'] = detail['image']
                detail.pop('image')
                book['details'] = detail
                results.append(book)

    return results


def get_html_container(url):
    ua = UserAgent()
    nbr_of_request = 0
    headers = {
        'user-agent': ua.random,
        'Referer': "http://libgen.rs/",
        'Host': 'libgen.rs',
                'Connection': 'keep-alive'}
    with requests.session() as session:
        r = session.get(url, headers=headers, timeout=TIMEOUT)
        while r.status_code != 200 and nbr_of_request <= MAX_REQUEST_TRY:
            headers = {
                'user-agent': ua.random,
                'Referer': "http://libgen.rs/",
                'Host': 'libgen.rs',
                'Connection': 'keep-alive'}
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            nbr_of_request = nbr_of_request + 1
    if nbr_of_request <= MAX_REQUEST_TRY:
        return r
    else:
        raise requests.ConnectionError
