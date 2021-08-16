import math
from bs4 import BeautifulSoup
from utils import create_url, get_html_container
import config


def search(url_params):
    url = create_url(config.NON_FICTION_BASE_URL, url_params)
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

        total_item_container = soup.find(
            "font", {'color': "grey", 'size': 1})
        table = soup.find("table", class_="c")

        if total_item_container:
            total_item = int(
                total_item_container.text.strip().split(" ")[0])
            total_item = total_item if total_item <= config.MAX_SHOWING_RESULTS else config.MAX_SHOWING_RESULTS
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
                        "image": config.IMAGE_SOURCE + rows[1].img['src'].strip(),
                        "download_links": [],
                        'year': year
                    }
                })
                books.append(book)

        results.update({
            'total_item': total_item,
            'total_pages': math.ceil(total_item / config.NON_FICTION_ITEMS_PER_PAGE),
            'items': books
        })
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
        r = get_html_container(config.NON_FICTION_LATEST, timeout=config.TIMEOUT)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        feed_entries = soup.find_all('item')

        for item in feed_entries:
            book = {}
            file_info = get_entry_details(
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
        raise e


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
    summary = soup.find_all('td')

    if summary[13].text.strip().lower() not in config.RSS_LANGUAGES:
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

        if extension not in config.EXTENSIONS:
            return None

        result.update({
            'language': summary[13].text.strip(),
            'size': file_info[0] + ' ' + file_info[1],
            'image': config.IMAGE_SOURCE + summary[0].img['src'],
            'extension': extension,
            'nbrOfPages': nbr_of_pages,
            'authors': summary[3].text.strip().split(','),
            'isbn': summary[5].text.strip().split(','),
            'series': summary[11].text.strip()
        })
    return result
    