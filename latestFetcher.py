from core import get_html_container
from bs4 import BeautifulSoup

VALID_RSS_LANGUAGE = {'french', 'english', 'français', 'anglais'}
NON_FICTION_LATEST = "http://libgen.rs/rss/index.php?page=20"
FICTION_LATEST = "http://libgen.rs/fiction/rss"
VALID_EXTENSION = {'pdf', 'epub', 'zip', 'rar',
                   'azw', 'azw3', 'fb2', 'mobi', 'djvu'}
TIMEOUT = 10
MAX_REQUEST_DETAILS_TRY = 10
MAX_REQUEST_TRY = 20
IMAGE_SOURCE = "https://libgen.is"


def get_non_fiction_latest_books():
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(NON_FICTION_LATEST)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        feed_entries = soup.find_all('item')

        for item in feed_entries:
            book = {}
            file_info = get_non_fiction_additionnal_info(
                item.description.text)
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
                        'type': 'non-fiction',
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
        raise Exception(e.__str__)


def get_fiction_latest_books():
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(FICTION_LATEST)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        feed_entries = soup.find_all('item')
        for item in feed_entries:
            book = {}
            file_info = get_fiction_additionnal_info(
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
        raise Exception


def get_non_fiction_additionnal_info(entries_summary):
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
    summary = soup.find_all('td')

    if summary[13].text.strip().lower() not in VALID_RSS_LANGUAGE:
        return None

    if len(summary) != 0:
        nbr_of_pages = ""

        nbr_of_pages_container = summary[1].find_all('i')
        if len(nbr_of_pages_container) != 0:
            temp = nbr_of_pages_container[-1].text.split(",")
            if 'pp' in temp[-1]:
                nbr_of_pages = temp[-1].strip().split(" ")[0]
            # Size + extension

        file_info = summary[7].text.strip().split(' ')

        extension = file_info[-1].replace('[', '').replace(']', '').lower()

        if extension not in VALID_EXTENSION:
            return None

        result.update({
            'language': summary[13].text.strip(),
            'size': file_info[0] + ' ' + file_info[1],
            'image': IMAGE_SOURCE + summary[0].img['src'],
            'extension': extension,
            'nbrOfPages': nbr_of_pages,
            'authors': summary[3].text.strip().split(','),
            'isbn': summary[5].text.strip().split(','),
            'series': summary[11].text.strip()
        })
    return result


def get_fiction_additionnal_info(entries_summary):
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
        if i*2 < _len and (i*2) + 1 < _len:
            key = summary[i*2].text.strip().lower().replace(':', '')
            value = summary[(i*2)+1].text.strip()

            if key == 'authors':
                value = value.split(',')

            elif key == 'file':
                value = value.split('/')
                result['size'] = value[-1].strip()
                if value[0].strip().lower() not in VALID_EXTENSION:
                    return None
                else:
                    result['extension'] = value[0].strip().lower()

            elif key == 'language':
                if value.lower() not in VALID_RSS_LANGUAGE:
                    return None

            if key != "file":
                result[key] = value
    return result
