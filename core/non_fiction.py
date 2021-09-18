import math

from bs4 import BeautifulSoup

from config import libgen_config as config
from cachetools import cached, TTLCache
from helpers import create_url, get_html_container, get_libgen_non_fiction_params, InvalidParamsError, checkIsbn, \
    get_book_details_by_type, get_libgen_lc_requests_params

non_fiction_cache = TTLCache(maxsize=128, ttl=config.CACHE_TTL)


def search(req_params):
    try:
        if req_params['language'] is not None and req_params['language'] != 'all':
            params = get_libgen_lc_requests_params(req_params)
            result = get_books_filtered_language(params)
        elif req_params['view'] == 'simple':
            params = get_libgen_non_fiction_params(req_params)
            result = get_list_from_simple_view(params)
        elif req_params['view'] == 'detailed':
            params = get_libgen_non_fiction_params(req_params)
            result = get_list_from_detailed_view(params)
        else:
            raise InvalidParamsError(['view'])
        return result
    except Exception as e:
        raise e


def get_list_from_detailed_view(url_params):
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
                rows = table.find_all("tr")

                page_language = rows[6].find_all("td")
                size_extension = rows[9].find_all("td")
                series = rows[3].find_all('td')[1].text.strip()
                publisher = rows[4].find_all('td')[1].text.strip()
                year = rows[5].find_all('td')[1].text.strip()
                isbns_id = rows[7].find_all(
                    'td')
                isbns = isbns_id[1].text.strip().replace(' ', '').split(',')
                libgen_id = isbns_id[3].text.strip()

                size_container = size_extension[1].text.strip().split(
                    ' ')

                book.update({
                    'libgenID': int(libgen_id),
                    'title': rows[1].b.text.strip(),
                    'md5': rows[1].a['href'].strip().split('=')[-1],
                    'language': page_language[1].text.strip(),
                    'size': size_container[0] + size_container[1],
                    'extension': size_extension[-1].text.strip(),
                    'source': '',
                    'nbrOfPages': page_language[-1].text.strip(),
                    "image": config.IMAGE_SOURCE + rows[1].img['src'].strip(),
                    'details': {
                        'authors': rows[2].b.text.strip().split(','),
                        'type': 'non-fiction',
                        'publisher': publisher,
                        'isbn': isbns,
                        "series": series,
                        'description': '',
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


def get_list_from_simple_view(url_params):
    url = create_url(config.NON_FICTION_BASE_URL, url_params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(
            url=url, timeout=config.TIMEOUT, max_requests_try=config.MAX_REQUESTS_TRY)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        total_item_container = soup.find(
            "font", {'color': "grey", 'size': 1})

        if total_item_container:
            total_item = int(
                total_item_container.text.strip().split(" ")[0])
            total_item = total_item if total_item <= config.MAX_SHOWING_RESULTS else config.MAX_SHOWING_RESULTS
            if total_item == 0:
                return results
        else:
            return results

        table = soup.find("table", class_="c")
        rows = table.find_all("tr")

        # remove the header of the table
        rows.pop(0)

        for row in rows:
            book = {}
            data = row.find_all("td")
            isbns = []
            language = data[6].text.strip()
            extension = data[8].text.strip()

            # remove the ISBN,Collection,edition from the title
            extra_data = data[2].find_all("i")
            title = data[2].text.strip()
            for _item in extra_data:
                temp = _item.text.strip()
                if checkIsbn(temp):
                    isbns.append(temp)
                elif checkIsbn(temp.replace('-', '')):
                    isbns.append(temp.replace("-", ""))
                title = title.replace(temp, "")

            md5 = data[9].a['href'].strip().split("/")[-1]

            book.update({
                'libgenID': int(data[0].text.strip()),
                'title': title.strip(),
                'language': language,
                'size': data[7].text.strip(),
                'extension': extension,
                'md5': md5,
                'image': '',
                'nbrOfPages': data[5].text.strip(),
                'series': '',
                'source': '',
                'details': {
                    'authors': data[1].text.strip().split(','),
                    'type': 'non-fiction',
                    'publisher': data[3].text.strip(),
                    'isbn': isbns,
                    "series": "",
                    'description': '',
                    "download_links": [],
                    'year': data[4].text.strip()
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


@cached(cache=non_fiction_cache)
def get_latest():
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }

    books = []

    try:
        r = get_html_container(config.NON_FICTION_LATEST,
                               timeout=config.TIMEOUT)

        html_text = r.text
        soup = BeautifulSoup(html_text, 'lxml')

        feed_entries = soup.find_all('item')

        for _item in feed_entries:
            if len(books) < config.MAX_NEW_ENTRY_IN_FICTION:
                book = {}
                file_info = get_book_details_from_rss_entry(
                    _item.description.text)
                if file_info:
                    book.update({
                        'libgenID': file_info['libgenID'],
                        'title': _item.title.text.strip(),
                        'language': file_info['language'],
                        'size': file_info['size'],
                        'extension': file_info['extension'],
                        'md5': _item.guid.text.strip(),
                        'source': 'recent',
                        'nbrOfPages': file_info['nbrOfPages'],
                        "image": file_info['image'],
                        'details': {
                            'authors': file_info['authors'],
                            'type': 'non-fiction',
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


def get_book_details_from_rss_entry(entries_summary):
    result = {
        'libgenID': '',
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
            'libgenID': int(summary[15].text.strip()),
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


def get_book_details(md5: str):
    return get_book_details_by_type('non-fiction', md5)


def get_books_filtered_language(params):
    headers = {
        'user-agent': '',
        'Host': 'libgen.lc',
        'Connection': 'keep-alive',
        'Accept': "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
    }
    url = create_url(config.LIBGEN_LC_URL,
                     params)
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []
    try:
        resp = get_html_container(url=url, timeout=config.TIMEOUT,
                                  max_requests_try=config.MAX_REQUESTS_TRY, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        spans = soup.find_all("span", class_="badge badge-primary")

        total_item = int(spans[1].text.strip())
        table = soup.find("table", class_="table table-striped")
        rows = table.find_all("tr")

        # remove the header of the table
        rows.pop(0)

        for row in rows:
            book = {}
            data = row.find_all("td")

            isbns = []
            language = data[6].text.strip()
            extension = data[8].text.strip()

            for anchor in data[1].find_all('a'):
                if anchor.text:
                    title = anchor.text
                    break

            # remove the ISBN,Collection,edition from the title
            extra_data = data[1].find(
                "font", {'color': 'green'}).text.strip().split(';')
            for _item in extra_data:
                temp = _item.strip()
                if checkIsbn(temp):
                    isbns.append(temp)
                elif checkIsbn(temp.replace('-', '')):
                    isbns.append(temp.replace("-", ""))
                title = title.replace(temp, "")

            md5 = data[9].a['href'].strip().split("=")[-1]

            book.update({
                'libgenID': '',
                'title': title.strip(),
                'language': language,
                'size': data[7].text.strip(),
                'extension': extension,
                'md5': md5,
                'image': config.LIBGEN_LC_IMAGE_SOURCE + data[0].img['src'].strip(),
                'nbrOfPages': data[5].text.strip(),
                'series': '',
                'source': '',
                'details': {
                    'authors': data[2].text.strip().split(','),
                    'type': 'non-fiction',
                    'publisher': data[3].text.strip(),
                    'isbn': isbns,
                    "series": "",
                    'description': '',
                    "download_links": [],
                    'year': data[4].text.strip()
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
