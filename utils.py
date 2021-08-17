from urllib.parse import urlencode
from fake_useragent import UserAgent
from requests import Session


class MaxRequestsTryError(Exception):
    def __init__(self, nbr_of_try, max_number_of_try):
        p = "tries" if max_number_of_try > 1 else "try"
        self.message = f"Max request try exceeded : {nbr_of_try}/{max_number_of_try} {p}"
        super().__init__(self.message)


class InvalidParamsError(Exception):
    def __init__(self, missing_params: list):
        message = "Missing params: "
        for i, param in enumerate(missing_params):
            message += f"{param}"
            if i % 2 == 0:
                message += ', '
        self.message = message
        super().__init__(self.message)


def create_url(base_url, params):
    encoded_params = ''
    if params and params != {}:
        encoded_params = urlencode(params)
    result = base_url + encoded_params
    return result


def get_html_container(url, timeout=10, max_requests_try=10):
    ua = UserAgent()
    nbr_of_request = 0
    headers = {
        'user-agent': ua.random,
        'Referer': "http://libgen.rs/",
        'Host': 'libgen.rs',
                'Connection': 'keep-alive'}
    try:
        with Session() as session:
            r = session.get(url, headers=headers, timeout=timeout)
            while r.status_code != 200 and nbr_of_request <= max_requests_try:
                headers = {
                    'user-agent': ua.random,
                    'Referer': "http://libgen.rs/",
                    'Host': 'libgen.rs',
                    'Connection': 'keep-alive'}
                r = session.get(url, headers=headers, timeout=timeout)
                nbr_of_request = nbr_of_request + 1
        if nbr_of_request <= max_requests_try:
            return r
        else:
            raise MaxRequestsTryError(nbr_of_request, max_requests_try)
    except Exception as e:
        raise e


def format_field(params: dict, field: str):
    result = params[field] if field in params and params[field] != "all" else ""
    return result


def get_libgen_fiction_params(params: dict):
    language = format_field(params, 'language')
    format = format_field(params, 'format')
    result = {}
    if 'q' not in params or 'page' not in params:
        raise InvalidParamsError(['q(query)', 'page'])
    else:
        result = {
            'q': params['q'],
            'criteria': '',
            'wildcard': 1,
            'language': language,
            'format': format,
            'page': params['page'],
        }

    return result


def get_libgen_non_fiction_params(params: dict):
    language = format_field(params, 'language')
    format = format_field(params, 'format')
    result = {}
    if 'q' not in params or 'page' not in params:
        raise InvalidParamsError(['q(query)', 'page'])
    else:
        result = {
            'req': params['q'],
            'open': 0,
            'res': 50,
            'view': 'detailed',
            'phrase': 0,
            'column': 'def',
            'language': language,
            'format': format,
            'page': params['page']
        }

    return result
