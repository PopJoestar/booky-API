from config.libgen_config import MAX_REQUESTS_TRY, \
    TIMEOUT, LIBGEN_LC_URL
from helpers import create_url, get_html_container, \
    get_libgen_lc_requests_params, parse_libgen_lc_result


def search(req_params):
    try:
        google_mode = req_params['language'] != 'all'
        params = get_libgen_lc_requests_params(
            req_params, topics='l,f', google_mode=google_mode)
        results = get_items(params)

        return results
    except Exception as e:
        raise e


def get_items(params):
    headers = {
        'user-agent': '',
        'Host': 'libgen.lc',
        'Connection': 'keep-alive',
        'Accept': "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
    }
    url = create_url(LIBGEN_LC_URL,
                     params)
    try:
        resp = get_html_container(url=url, timeout=TIMEOUT,
                                  max_requests_try=MAX_REQUESTS_TRY, headers=headers)
        return parse_libgen_lc_result(resp)
    except Exception as e:
        raise e
