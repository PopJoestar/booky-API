import math
from re import compile, sub
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from iso639 import Lang
from requests import Session

from config.libgen_config import FICTION_DETAILS_BASE_URL, IMAGE_SOURCE, MAX_DETAILS_REQUESTS_TRY, MAX_REQUESTS_TRY, \
    NON_FICTION_DETAILS_URL, TIMEOUT, LIBGEN_LC_IMAGE_SOURCE


def create_url(base_url, params):
    encoded_params = ''
    if params and params != {}:
        encoded_params = urlencode(params)
    result = base_url + encoded_params
    return result


def get_html_container(url, timeout=10, max_requests_try=10, headers=None):
    if headers is None:
        headers = {
            'user-agent': '',
            'Referer': "http://libgen.rs/",
            'Host': 'libgen.rs',
            'Connection': 'keep-alive',
            'Accept': "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
        }
    ua = UserAgent()
    nbr_of_request = 0
    headers['user-agent'] = ua.random

    try:
        with Session() as session:
            resp = session.get(url, headers=headers, timeout=timeout)
            while resp.status_code != 200 and nbr_of_request <= max_requests_try:
                headers['user-agent'] = ua.random
                resp = session.get(url, headers=headers, timeout=timeout)
                nbr_of_request = nbr_of_request + 1
        if nbr_of_request <= max_requests_try:
            # r.raw.chunked = True  # Fix issue 1
            # r.encoding = 'utf-8'  # Fix issue 2
            return resp
        else:
            from helpers.exceptions import MaxRequestsTryError
            raise MaxRequestsTryError(nbr_of_request, max_requests_try)
    except Exception as e:
        raise e


def format_field(params: dict, field: str):
    result = params[field] if field in params and params[field] != "all" else ""
    return result


def get_libgen_fiction_params(params: dict):
    language = format_field(params, 'language').capitalize()
    _format = format_field(params, 'format')
    if 'q' not in params or 'page' not in params or 'view' not in params:
        from helpers.exceptions import InvalidParamsError
        raise InvalidParamsError(['q(query)', 'page', 'view'])
    else:
        result = {
            'q': params['q'],
            'criteria': '',
            'wildcard': 1,
            'language': language,
            'format': _format,
            'page': params['page'],
        }

    return result


def get_libgen_lc_requests_params(params: dict, topics: str = 'l', google_mode: bool = True):
    _topics = topics.split(',')
    if 'q' not in params or 'page' not in params or 'language' not in params:
        from helpers.exceptions import InvalidParamsError
        raise InvalidParamsError(['q(query)', 'page', 'language'])
    else:
        language = format_field(params, 'language').capitalize()
        if google_mode:
            req = f"{params['q']} lang:{Lang(language).pt2b}"
        else:
            req = params['q']
        result = [
            ('req', req),
            ('columns[]', 't,a,s,y,p,i'),
            ('objects[]', 'f'),
            ('objects[]', 'e'),
            ('objects[]', 's'),
            ('objects[]', 'a'),
            ('objects[]', 'p'),
            ('topics[]', _topics[0]),
            ('topics[]', _topics[-1]),
            ('res', 25),
            ('curetab', 'f'),
            ('covers', 'on'),
            ("gmode", "on"),
            ("filesuns", "off"),
            ('page', params['page']),
        ]

    return result


def get_libgen_non_fiction_params(params: dict):
    language = format_field(params, 'language')
    _format = format_field(params, 'format')
    if 'q' not in params or 'page' not in params or 'view' not in params:
        from helpers.exceptions import InvalidParamsError
        raise InvalidParamsError(['q(query)', 'page', 'view'])
    else:
        result = {
            'req': params['q'],
            'open': 0,
            'res': 25,
            'view': params['view'],
            'phrase': 0,
            'column': 'def',
            'language': language,
            'format': _format,
            'page': params['page']
        }

    return result


def checkIsbn(subject):
    result: bool = True

    # Checks for ISBN-10 or ISBN-13 format
    regex = compile("^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$"
                    "|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$"
                    "|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?"
                    "[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$")

    if regex.search(subject):
        # Remove non ISBN digits, then split into a list
        chars = list(sub("[- ]|^ISBN(?:-1[03])?:?", "", subject))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last = chars.pop()

        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            val = sum((x + 2) * int(y) for x, y in enumerate(reversed(chars)))
            check = 11 - (val % 11)
            if check == 10:
                check = "X"
            elif check == 11:
                check = "0"
        else:
            # Compute the ISBN-13 check digit
            val = sum((x % 2 * 2 + 1) * int(y) for x, y in enumerate(chars))
            check = 10 - (val % 10)
            if check == 10:
                check = "0"

        if str(check) != last:
            result = False
    else:
        result = False

    return result


def get_details(session, book_md5, book_type, ua):
    is_fiction = book_type == 'fiction'
    nbr_of_request = 0
    url = FICTION_DETAILS_BASE_URL if is_fiction else NON_FICTION_DETAILS_URL
    url = url + book_md5
    headers = {
        'user-agent': ua.random,
        'Referer': 'http://libgen.rs/',
        'Host': 'library.lol',
        'Connection': 'keep-alive',
        'Accept': "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
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
    download_links = []

    try:

        r = session.get(url, headers=headers, timeout=TIMEOUT)

        while r.status_code != 200 and nbr_of_request <= MAX_DETAILS_REQUESTS_TRY:
            headers = {
                'user-agent': ua.random,
                'Referer': 'http://libgen.rs/',
                'Host': 'library.lol',
                'Connection': 'keep-alive',
                'Accept': "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Upgrade-Insecure-Requests": "1"
            }
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            nbr_of_request = nbr_of_request + 1

        if nbr_of_request <= MAX_REQUESTS_TRY:
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


def get_book_details_by_type(_type: str, md5: str):
    ua = UserAgent()
    result = {}

    with Session() as session:
        temp = get_details(session, md5, _type, ua)
        if temp:
            for i, key in enumerate(temp):
                if i:
                    result[key] = temp[key]
    return result


def parse_libgen_lc_result(resp):
    results = {
        'total_item': 0,
        'total_pages': 1,
        'items': []
    }
    books = []
    html_text = resp.text
    title = ''
    soup = BeautifulSoup(html_text, 'lxml')

    spans = soup.find_all("span", class_="badge badge-primary")

    total_item = int(spans[0].text.strip())
    table = soup.find("table", class_="table table-striped")
    if table:
        rows = table.find_all("tr")

        # remove the header of the table
        rows.pop(0)

        for row in rows:
            book = {}
            data = row.find_all("td")

            isbns = []
            language = data[5].text.strip()
            extension = data[8].text.strip()
            type_container = data[1].find(
                'span', class_="badge badge-secondary").text.strip()
            _type = 'non-fiction' if 'l' in type_container else 'fiction'
            for anchor in data[1].find_all('a'):
                if anchor.text:
                    title = anchor.text
                    break

            # remove the ISBN,Collection,edition from the title
            extra_data = data[1].find(
                "font", {'color': 'green'})
            if extra_data:
                for _item in extra_data.text.strip().split(';'):
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
                'image': LIBGEN_LC_IMAGE_SOURCE + data[0].img['src'].strip(),
                'nbrOfPages': data[6].text.strip(),
                'series': '',
                'source': '',
                'details': {
                    'authors': data[2].text.strip().split(','),
                    'type': _type,
                    'publisher': data[3].text.strip(),
                    'isbn': isbns,
                    "series": "",
                    'description': '',
                    "download_links": [],
                    'year': data[4].text.strip()
                }
            })
            books.append(book)
        total_pages = math.ceil(total_item / 25)
        results.update({
            'total_item': total_item,
            'total_pages': total_pages if total_pages < 40 else 40,
            'items': books
        })
    return results
