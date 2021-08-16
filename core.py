from bs4 import BeautifulSoup
from fake_useragent.fake import UserAgent
import requests
from config import FICTION_DETAILS_BASE_URL, IMAGE_SOURCE, MAX_DETAILS_REQUESTS_TRY, MAX_REQUESTS_TRY, NON_FICTION_DETAILS_URL, TIMEOUT


def get_details(session, book_md5, book_type, ua):
    is_fiction = book_type == 'fiction'
    nbr_of_request = 0
    url = FICTION_DETAILS_BASE_URL if is_fiction else NON_FICTION_DETAILS_URL
    url = url + book_md5

    headers = {
        'user-agent': ua.random,
        'Referer': 'http://libgen.rs/',
        'Host': 'library.lol',
        'Connection': 'keep-alive'
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

        while r.status_code != 200 and nbr_of_request <= MAX_DETAILS_REQUESTS_TRY:
            headers = {
                'user-agent': ua.random,
                'Referer': 'http://libgen.rs/',
                'Host': 'library.lol',
                'Connection': 'keep-alive'
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


def get_book_details(type: str,  md5: str):
    ua = UserAgent()
    with requests.Session() as session:
        results = get_details(session, md5, type, ua)
    return results
