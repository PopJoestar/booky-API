import json

from falcon import HTTP_503, HTTP_500, HTTP_400
from requests import ConnectionError, Timeout

from core.fiction import search, get_latest, get_latest_from_rss, get_book_details
from helpers import InvalidParamsError, MaxRequestsTryError


class Fiction:
    @staticmethod
    def on_get(req, resp):
        try:
            result = search(req_params=req.params)
        except InvalidParamsError as e:
            result = {
                'error': e.message
            }
            resp.status = HTTP_400
        except (ConnectionError, Timeout, MaxRequestsTryError) as e:
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

    @staticmethod
    def on_get_latest(req, resp):
        try:
            result = get_latest()
        except (ConnectionError, Timeout, MaxRequestsTryError) as e:
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

    @staticmethod
    def on_get_latest_from_rss(req, resp):

        try:
            result = get_latest_from_rss()
        except (ConnectionError, Timeout, MaxRequestsTryError) as e:
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

    @staticmethod
    def on_get_details(req, resp, md5):
        result = get_book_details(md5)
        if not result:
            result = {'error': "Couldn't connect to libgen"}
            resp.status = HTTP_503
        resp.text = json.dumps(result)
