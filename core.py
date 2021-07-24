import concurrent.futures
import math
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from latestFetcher import get_non_fiction_latest_book_list

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
    if params is not None and params != {}:
        encoded_params = urlencode(params)
    result = base_url + encoded_params
    return result


# get the details of a book
def get_book_details(session, book_md5, is_fiction, ua):
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
        'type': 'fiction' if is_fiction else 'non-fiction',
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

            if details_container is not None:
                image = IMAGE_SOURCE + details_container.img['src']
                details = details_container.find_all('p')

                # get the description if exist
                description_container = details_container.find_all("div")
                if len(description_container) > 3:
                    result.update({
                        'description': str(description_container[3])
                    })
                else:
                    if description_container[-1].text != "":
                        result.update({
                            'description': str(description_container[-1])
                        })

                # get Author(s), Publisher, ISBN
                for detail in details:
                    if 'Author(s)' in detail.text:
                        res = detail.text.split(":")
                        result.update({
                            'authors': item.split(',') for item in res[-1].strip().split(";")
                        })
                    elif 'Publisher' in detail.text:
                        res = detail.text.split(":")
                        result.update({
                            'publisher': res[1].strip().split(",")[0],
                        })
                        if not is_fiction:
                            value = res[-1].strip()
                            result.update({
                                'year': value if value != "" and value.isdigit() else ''
                            })
                    elif 'ISBN' in detail.text:
                        res = detail.text.split(":")
                        value = res[-1].strip().split(",") if res[-1] != "" else []
                        if value:
                            result.update({
                                'isbn': res[-1].strip().split(",")
                            })
                    elif 'Series' in detail.text:
                        res = detail.text.split(":")
                        result.update({
                            'series': res[-1].strip()
                        })
                    if is_fiction:
                        if 'Year' in detail.text:
                            res = detail.text.split(":")
                            result.update({
                                'year': res[-1].strip()
                            })
                # get all available download links
                download_container = soup.find(
                    'div', id="download").find_all('a')
                download_links = []
                if download_container is not None:
                    for link in download_container:
                        download_links.append(link['href'])

                result.update({
                    'image': image,
                    'download_links': download_links
                })
            else:
                return 404
        else:
            return 502
    except requests.Timeout as e:
        return 504
    except Exception as e:
        return 503
    else:
        return result


def get_additionnal_non_fiction_book_details(non_fiction_book_md5):
    nbr_of_request = 0
    url = NON_FICTION_DETAILS_URL + non_fiction_book_md5
    ua = UserAgent()
    headers = {
        'user-agent': ua.random,
        'Referer': 'http://libgen.rs/',
        'Host': 'library.lol',
    }

    result = {
        'description': "",
        "download_links": [],
        'year': ''
    }

    try:
        with requests.session() as session:
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

            if details_container is not None:
                details = details_container.find_all('p')

                # get the description if exist
                description_container = details_container.find_all("div")
                if len(description_container) > 3:
                    result.update({
                        'description': str(description_container[3])
                    })
                else:
                    if description_container[-1].text != "":
                        result.update({
                            'description': str(description_container[-1])
                        })

                for detail in details:
                    if 'Publisher' in detail.text:
                        res = detail.text.split(":")
                        value = res[-1].strip()
                        result.update({
                            'year': value if value != "" and value.isdigit() else ''
                        })

                # get all available download links
                download_container = soup.find(
                    'div', id="download").find_all('a')
                download_links = []
                if download_container is not None:
                    for link in download_container:
                        download_links.append(link['href'])

                result.update({
                    'download_links': download_links
                })
            else:
                return 404
        else:
            return 502
    except requests.Timeout as e:
        return 504
    except Exception as e:
        return 503
    else:
        return result


def get_non_fiction_book_list(url_params):
    url = create_url(NON_FICTION_BASE_URL, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'type': 'non-fiction',
        'items': []
    }
    ua = UserAgent()
    books = []
    nbr_of_request = 0

    headers = {
        'user-agent': ua.random,
        'Referer': "http://libgen.rs/",
        'Host': 'libgen.rs',
        'Connection': 'keep-alive'
    }

    try:
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
            html_text = r.text
            soup = BeautifulSoup(html_text, 'lxml')

            total_item_container = soup.find(
                "font", {'color': "grey", 'size': 1})
            table = soup.find("table", class_="c")

            if total_item_container is not None:
                total_item = int(
                    total_item_container.text.strip().split(" ")[0])
                total_item = total_item if total_item <= MAX_SHOWING_RESULTS else MAX_SHOWING_RESULTS
                if total_item == 0:
                    return 404
            else:
                return 404

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

    except requests.Timeout as e:
        return 504
    except Exception as e:
        return 503
    else:
        return results


# return an array of fiction_book according to the url_params: array of book{title,language,size,extension,md5}
def get_fiction_book_list(session, url, url_params, ua):
    url = create_url(url, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []
    nbr_of_request = 0
    headers = {
        'user-agent': ua.random,
        'Referer': "http://libgen.rs/",
        'Host': 'libgen.rs',
        'Connection': 'keep-alive'
    }
    try:
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
            html_text = r.text
            soup = BeautifulSoup(html_text, 'lxml')
            non_break_space = u'\xa0'

            table = soup.find("table", class_="catalog")
            total_items_container = soup.find("div", style="float:left")

            if total_items_container is not None:
                total_items = int(total_items_container.text.strip().split(" ")[
                    0].replace(non_break_space, ''))
                results.update({
                    'total_item': total_items,
                    'total_pages': math.ceil(total_items / MAX_ITEMS_PER_PAGE)
                })
            else:
                return 404

            if table is not None:
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
                            'details': None
                        })
                        books.append(book)
                results.update({
                    'items': books
                })
            else:
                return 404
        else:
            return 502
    except requests.Timeout as e:
        return 504
    except Exception as e:
        return 503

    else:
        return results


# return an array of book with details: array of book{title,language,size,extension,md5,details}
def get_books(is_fiction, url_params=None, is_latest=False):
    book_details = []
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    ua = UserAgent()

    # using thread to get details for each book in books
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        with requests.session() as session:
            if is_latest:
                books = get_fiction_book_list(session, FICTION_LATEST, url_params,
                                              ua) if is_fiction else get_non_fiction_latest_book_list(ua)
            else:
                books = get_fiction_book_list(session, FICTION_BASE_URL, url_params,
                                              ua)

            if not isinstance(books, int) and len(books['items']) != 0:
                md5s = [book['md5'] for book in books['items']]
                temp = {executor.submit(
                    get_book_details, session, md5, is_fiction, ua): md5 for md5 in md5s}
                for future in concurrent.futures.as_completed(temp):
                    try:
                        data = future.result(timeout=TIMEOUT)
                    except Exception as e:
                        pass
                    else:
                        if not isinstance(data, int):
                            book_details.append(data)

                # map detail to book
                for book in books['items']:
                    for detail in book_details:
                        if book["md5"] in detail:
                            detail.pop(book['md5'])
                            book.update({
                                'image': detail['image']
                            })
                            detail.pop('image')
                            book.update({
                                'details': detail
                            })
                            results['items'].append(book)

                results.update(
                    {'total_pages': books['total_pages'], 'total_item': books['total_item']})
            else:
                return books

    return results
