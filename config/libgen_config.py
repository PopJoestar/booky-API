import os

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

dir_path = os.path.dirname(os.path.realpath(__file__))
config = os.path.join(dir_path, "config.yaml")
with open(config) as conf_file:
    conf = safe_load(conf_file)
    FICTION_LATEST = conf.get('FICTION_LATEST')
    FICTION_RSS = conf.get('FICTION_RSS')
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
    MAX_NEW_ENTRY_IN_FICTION = conf.get("MAX_NEW_ENTRY_IN_FICTION")

    NON_FICTION_ITEMS_PER_PAGE = conf.get(
        "NON_FICTION_ITEMS_PER_PAGE")
    MAX_SHOWING_RESULTS = conf.get("MAX_SHOWING_RESULTS")
    CACHE_TTL = conf.get("CACHE_TTL")
