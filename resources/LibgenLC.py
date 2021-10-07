import json

from falcon import HTTP_503, HTTP_500, HTTP_400
from requests import ConnectionError, Timeout

from core.libgenLC import search
from helpers import InvalidParamsError, MaxRequestsTryError


class LibgenLC:
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
