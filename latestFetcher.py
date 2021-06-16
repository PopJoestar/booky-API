import feedparser
from bs4 import BeautifulSoup

VALID_RSS_LANGUAGE = {'french', 'english'}
NON_FICTION_LATEST = "http://libgen.rs/rss/index.php?page=20"
VALID_EXTENSION = {'pdf', 'epub', 'zip', 'rar', 'azw', 'azw3', 'fb2', 'mobi', 'djvu'}

# get all recently added books
def get_non_fiction_latest_book_list(user_agent):
    results = {
        'total_item': 0,
        'total_pages': 1,
        'type': 'non-fiction',
        'items': []
    }

    header = {
        "user-agent": user_agent.random,
        'Referer': "http://libgen.rs/",
        'Host': 'libgen.rs',
        'Connection': 'keep-alive'}

    books = []

    try:
        feed = feedparser.parse(NON_FICTION_LATEST, request_headers=header)

        for item in feed.entries:
            book = {}
            file_info = get_non_fiction_additionnal_info(item.summary)
            if file_info != -1:
                if file_info['language'].lower() in VALID_RSS_LANGUAGE and file_info['extension'].lower() in VALID_EXTENSION:
                    book.update({
                        'title': item.title.strip(),
                        'language': file_info['language'],
                        'size': file_info['size'],
                        'extension': file_info['extension'],
                        'md5': item.id.strip(),
                        'image': '',
                        'nbrOfPages': file_info['nbrOfPages'],
                        'series': '',
                        'source': '',
                        'details': None
                    })
                    books.append(book)
                if len(books) == 15:
                    break
        results.update({
            'total_item': len(books),
            'items': books
        })
    except Exception as e:
        return 502
    else:
        return results


# get language, size and extension from the html part of the rss feed
def get_non_fiction_additionnal_info(entries_summary):
    result = {
        'language': '',
        'size': '',
        'extension': '',
        'nbrOfPages': ''
    }
    soup = BeautifulSoup(entries_summary, 'lxml')
    summary = soup.find_all('td')

    if summary[13].text.strip().lower() not in VALID_RSS_LANGUAGE:
        return -1

    if len(summary) != 0:
        nbr_of_pages = ""

        nbr_of_pages_container = summary[1].find_all('i')
        if len(nbr_of_pages_container) != 0:
            temp = nbr_of_pages_container[-1].text.split(",")
            if 'pp' in temp[-1]:
                nbr_of_pages = temp[-1].strip().split(" ")[0]
            # Size + extension

        file_info = summary[7].text.strip().split(' ')

        result.update({
            'language': summary[13].text.strip(),
            'size': file_info[0] + ' ' + file_info[1],
            'extension': file_info[-1].replace('[', '').replace(']', '').lower(),
            'nbrOfPages': nbr_of_pages
        })
    return result
