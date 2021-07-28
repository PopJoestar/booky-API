from fake_useragent.fake import UserAgent
import requests
from latestFetcher import get_fiction_latest_books, get_non_fiction_latest_books
from flask import Flask, jsonify, request, abort
import core

app = Flask(__name__)


@app.route("/books/fiction", methods=['GET'])
def get_fiction_books():
    language = request.args.get(
        'language') if request.args.get('language') else ''
    language = '' if language == "all" else language

    _format = request.args.get('format') if request.args.get('format') else ''
    _format = '' if _format == "all" else _format

    params = {
        'q': request.args.get('q'),
        'criteria': '',
        'wildcard': 1,
        'language': language,
        'format': _format,
        'page': request.args.get('page'),
    }
    results = core.get_fiction_books(params)

    if isinstance(results, int):
        abort(results)
    return jsonify(results)


@app.route("/books/non-fiction", methods=['GET'])
def get_non_fiction_books():
    language = request.args.get(
        'language') if request.args.get('language') else ''
    language = '' if language == "all" else language

    _format = request.args.get('format') if request.args.get('format') else ''
    _format = '' if _format == "all" else _format
    params = {
        'req': request.args.get('q'),
        'open': 0,
        'res': 50,
        'view': 'detailed',
        'phrase': 0,
        'column': 'def',
        'language': language,
        'format': _format,
        'page': request.args.get('page'),
        'sort': 'id',
        'sortmode': 'DESC'
    }
    results = core.get_non_fiction_books(url_params=params)
    if isinstance(results, int):
        abort(results)
    return jsonify(results)


@app.route('/books/latest/fiction', methods=['GET'])
def get_latest_fiction():
    results = get_fiction_latest_books()
    return jsonify(results)


@app.route('/books/latest/non-fiction', methods=['GET'])
def get_latest_non_fiction():
    results = get_non_fiction_latest_books()
    return jsonify(results)


@app.route('/books/detail/<string:type>/<string:md5>', methods=['GET'])
def get_book_details(type: str, md5: str):
    ua = UserAgent()
    with requests.session() as session:
        results = core.get_book_details(session, md5, type, ua)
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
