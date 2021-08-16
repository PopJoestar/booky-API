import requests
import utils as my_utils
import fiction as fiction_module
import non_fiction as non_fiction_module
from wsgiref.simple_server import make_server
import falcon
import json


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
            resp.status = falcon.HTTP_400
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_500
        resp.text = json.dumps(result)

    def on_get_latest(self, req, resp):
        result = {}
        try:
            result = fiction_module.get_latest()
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_500
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
            resp.status = falcon.HTTP_400
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_500
        resp.text = json.dumps(result)

    def on_get_latest(self, req, resp):
        result = {}
        try:
            result = non_fiction_module.get_latest()
        except (requests.ConnectionError, requests.Timeout, my_utils.MaxRequestsTryError) as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_503
        except Exception as e:
            result = {
                'error': f"An exception of type {type(e).__name__} occurred: {e.args}"
            }
            resp.status = falcon.HTTP_500
        resp.text = json.dumps(result)


app = falcon.App()


fiction = Fiction()
non_fiction = NonFiction()


app.add_route('/books/fiction', fiction)
app.add_route('/books/fiction/latest', fiction, suffix='latest')

app.add_route('/books/non-fiction', non_fiction)
app.add_route('/books/non-fiction/latest', non_fiction, suffix='latest')


if __name__ == '__main__':
    with make_server('192.168.88.15', 5000, app) as httpd:
        print('Serving on port 5000...')

        # Serve until process is killed
        httpd.serve_forever()
