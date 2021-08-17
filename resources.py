import requests
import utils as my_utils
import fiction as fiction_module
import non_fiction as non_fiction_module
import json
from falcon import HTTP_503, HTTP_500, HTTP_400
from core import get_book_details


class Fiction:
    def on_get(self, req, resp):
        result = {}
        try:
            params = my_utils.get_libgen_fiction_params(req.params)
            result = fiction_module.search(params)
        except my_utils.InvalidParamsError as e:
            result = {
                'error': e.message
            }
            resp.status = HTTP_400
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_500
        resp.text = json.dumps(result)

    def on_get_latest(self, req, resp):
        result = {}
        try:
            result = fiction_module.get_latest()
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_500
        resp.text = json.dumps(result)

    def on_get_details(self, req, resp, md5):
        result = {}
        result = get_book_details('fiction', md5)
        if not result:
            result = {'error': "Couldn't connect to libgen"}
            resp.status = HTTP_503
        resp.text = json.dumps(result)


class NonFiction:
    def on_get(self, req, resp):
        result = {}
        try:
            params = my_utils.get_libgen_non_fiction_params(req.params)
            result = non_fiction_module.search(params)
        except my_utils.InvalidParamsError as e:
            result = {
                'error': e.message
            }
            resp.status = HTTP_400
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_500
        resp.text = json.dumps(result)

    def on_get_latest(self, req, resp):
        result = {}
        try:
            result = non_fiction_module.get_latest()
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = HTTP_500
        resp.text = json.dumps(result)

    def on_get_details(self, req, resp, md5):
        result = {}
        result = get_book_details('non-fiction', md5)
        if not result:
            result = {'error': "Couldn't connect to libgen"}
            resp.status = HTTP_503
        resp.text = json.dumps(result)
