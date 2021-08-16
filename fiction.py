from core import get_details
import math
from fake_useragent.fake import UserAgent
import requests
from bs4 import BeautifulSoup
from utils import create_url, get_html_container
import config
import gevent


def search(url_params):
    url = create_url(config.FICTION_BASE_URL, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []

    try:
        r = get_html_container(url, config.TIMEOUT, config.MAX_REQUESTS_TRY)

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
                        'title': data[2].text.strip(),
                        'language': language,
                        'size': file_info[-1].strip().replace(non_break_space, ''),
                        'extension': extension,
                        'md5': md5,
                        'nbrOfPages': '',
                        'source': 'recent' if url == config.FICTION_LATEST else '',
                        'image': '',
                        'details':
                            {'type': 'fiction'}
                    })
                    books.append(book)

            results['items'] = get_books_details(books)

        return results

    except Exception as e:
        raise e


def get_latest():
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(config.FICTION_LATEST)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')
        feed_entries = soup.find_all('item')
        for item in feed_entries:
            book = {}
            file_info = get_entry_details(
                item.description.text.strip())
            if file_info:
                book.update({
                    'title': item.title.text.strip(),
                    'language': file_info['language'],
                    'size': file_info['size'],
                    'extension': file_info['extension'],
                    'md5': item.guid.text.strip(),
                    'nbrOfPages': file_info['nbrOfPages'],
                    'source': '',
                    'details': {
                        'authors': file_info['authors'],
                        'type': 'fiction',
                        'publisher': '',
                        'isbn': file_info['isbn'],
                        "series": file_info['series'],
                        'description': "",
                        "image": file_info['image'],
                        "download_links": [],
                        'year': ''
                    }
                })
                books.append(book)
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

    with requests.Session() as session:
        threads = {gevent.spawn(
            get_details, session, book['md5'], book['details']['type'], ua): book for book in books}
        gevent.joinall(threads)

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


def get_entry_details(entries_summary):
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
        if (i*2) + 1 < _len:
            key = summary[i*2].text.strip().lower().replace(':', '')
            value = summary[(i*2)+1].text.strip()

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


if __name__ == '__main__':
    s = ['id', 'title', 'series', 'author', 'year', 'edition', 'publisher', 'pages',
         'language', 'identifier', 'filesize', 'extension', 'md5', 'coverurl', 'descr', 'toc', 'ipfs_cid']
    print(','.join([item.lower() for item in s]))
