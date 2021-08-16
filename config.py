from yaml import safe_load

EXTENSIONS = (
    'pdf',
    'epub',
    'zip',
    'rar',
    'azw',
    'azw3',
    'fb2',
    'mobi',
    'djvu'
)

LANGUAGES = (
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
    'polish'
)

RSS_LANGUAGES = ('french',
                 'english',
                 'français',
                 'anglais')


with open('./conf/config.yaml') as conf_file:
    conf = safe_load(conf_file)
    FICTION_LATEST = conf.get('FICTION_LATEST')
    FICTION_BASE_URL = conf.get("FICTION_BASE_URL")
    FICTION_DETAILS_BASE_URL = conf.get(
        "FICTION_DETAILS_BASE_URL")

    NON_FICTION_LATEST = conf.get('NON_FICTION_LATEST')
    NON_FICTION_BASE_URL = conf.get("NON_FICTION_BASE_URL")
    NON_FICTION_DETAILS_URL = conf.get("NON_FICTION_DETAILS_URL")

    IMAGE_SOURCE = conf.get("IMAGE_SOURCE")

    TIMEOUT = conf.get("TIMEOUT")
    MAX_DETAILS_REQUESTS_TRY = conf.get(
        "MAX_DETAILS_REQUESTS_TRY")
    MAX_REQUESTS_TRY = conf.get("MAX_REQUESTS_TRY")
    FICTION_ITEMS_PER_PAGE = conf.get("FICTION_ITEMS_PER_PAGE")
    NON_FICTION_ITEMS_PER_PAGE = conf.get(
        "NON_FICTION_ITEMS_PER_PAGE")
    MAX_SHOWING_RESULTS = conf.get("MAX_SHOWING_RESULTS")
