import math

from bs4 import BeautifulSoup
from fake_useragent.fake import UserAgent
from gevent import spawn, joinall
from requests import Session
from config import libgen_config as config
from cachetools import cached, TTLCache
from helpers import get_details, get_libgen_fiction_params, InvalidParamsError, get_book_details_by_type, create_url, \
    get_html_container
    
cache = TTLCache(maxsize=128, ttl=config.CACHE_TTL)

def search(req_params):
    try:
        params = get_libgen_fiction_params(req_params)
        if req_params['view'] == 'simple':
            result = search_without_details(params)
        elif req_params['view'] == 'detailed':
            result = search_with_details(params)
        else:
            raise InvalidParamsError(['view'])
        return result
    except Exception as e:
        raise e


def search_with_details(url_params):
    try:
        results = search_without_details(url_params)
        if len(results['items']) != 0:
            results['items'] = get_books_details(results['items'])
        return results
    except Exception as e:
        raise e


def search_without_details(url_params):
    url = create_url(config.FICTION_BASE_URL, url_params)
    try:
        r = get_html_container(url, config.TIMEOUT, config.MAX_REQUESTS_TRY)
        results = parse_libgen_response(resp=r)
        return results
    except Exception as e:
        raise e


def get_latest():
    try:
        r = get_html_container(
            config.FICTION_LATEST, config.TIMEOUT, config.MAX_REQUESTS_TRY)

        results = parse_libgen_response(resp=r)
        if len(results['items']) != 0:
            results['items'] = get_books_details(results['items'])
        return results
    except Exception as e:
        raise e


@cached(cache=cache)
def get_latest_from_rss():
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(config.FICTION_RSS)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')
        feed_entries = soup.find_all('item')
        for item in feed_entries:
            if len(books) < config.MAX_NEW_ENTRY_IN_FICTION:
                book = {}
                file_info = get_book_details_from_rss_entry(
                    item.description.text.strip())
                if file_info:
                    book.update({
                        'libgenID': None,
                        'title': item.title.text.strip(),
                        'language': file_info['language'],
                        'size': file_info['size'],
                        'extension': file_info['extension'],
                        'md5': item.guid.text.strip(),
                        'nbrOfPages': file_info['nbrOfPages'],
                        'source': 'recent',
                        "image": file_info['image'],
                        'details': {
                            'authors': file_info['authors'],
                            'type': 'fiction',
                            'publisher': "",
                            'isbn': file_info['isbn'],
                            "series": file_info['series'],
                            'description': "",
                            "download_links": [],
                            'year': ""
                        }
                    })
                    books.append(book)
            else:
                break
        results.update({
            'total_item': len(books),
            'items': books
        })
        return results
    except Exception as e:
        raise e


def get_books_details(books: list):
    ua = UserAgent()
    book_details = []
    results = []
    
    with Session() as session:
        threads = {spawn(
            get_details, session, book['md5'], book['details']['type'], ua): book for book in books}
        joinall(threads)

    for thread in threads:
        if thread.value:
            book_details.append(thread.value)

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


def get_book_details_from_rss_entry(entries_summary):
    result = {
        'language': '',
        'size': '',
        'extension': '',
        'nbrOfPages': '',
        'image': '',
        'series': '',
        'isbn': []
    }

    soup = BeautifulSoup(entries_summary, 'lxml')
    container = soup.find_all('td')

    summary = container[1].find_all('td')
    result['image'] = container[0].img['src']

    _len = len(summary)
    for i in range(_len):
        if (i * 2) + 1 < _len:
            key = summary[i * 2].text.strip().lower().replace(':', '')
            value = summary[(i * 2) + 1].text.strip()

            if key == 'authors':
                value = value.split(',')

            elif key == 'file':
                value = value.split('/')
                result['size'] = value[-1].strip()
                if value[0].strip().lower() not in config.EXTENSIONS:
                    return None
                else:
                    result['extension'] = value[0].strip().lower()

            elif key == 'language':
                if value.lower() not in config.RSS_LANGUAGES:
                    return None

            if key != "file":
                result[key] = value
    return result


def parse_libgen_response(resp):
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []
    html_text = resp.text
    soup = BeautifulSoup(html_text, 'lxml')

    non_break_space = u'\xa0'

    table = soup.find("table", class_="catalog")
    total_items_container = soup.find("div", style="float:left")

    if total_items_container:
        total_items = int(total_items_container.text.strip().split(" ")[
                              0].replace(non_break_space, ''))
        results.update({
            'total_item': total_items,
            'total_pages': math.ceil(total_items / config.FICTION_ITEMS_PER_PAGE)
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

            if extension.lower() in config.EXTENSIONS and language.lower() in config.LANGUAGES:
                md5 = data[5].ul.li.a['href'].strip().split("/")[-1]
                book.update({
                    'libgenID': "",
                    'title': data[2].text.strip(),
                    'language': language,
                    'source': '',
                    'size': file_info[-1].strip().replace(non_break_space, ''),
                    'extension': extension,
                    'md5': md5,
                    'nbrOfPages': "",
                    'image': "",
                    'details': {
                        'authors': data[0].text.strip().split(','),
                        'type': 'fiction',
                        'publisher': "",
                        'isbn': [],
                        "series": "",
                        'description': '',
                        "download_links": [],
                        'year': ""
                    }
                })
                books.append(book)

        results['items'] = books

    return results


def get_book_details(md5: str):
    return get_book_details_by_type('fiction', md5)