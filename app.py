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
    results = core.get_books(url_params=params, is_fiction=True)
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
        'res': 25,
        'view': 'simple',
        'phrase': 0,
        'column': 'def',
        'language': language,
        'format': _format,
        'page': request.args.get('page'),
        'sort': 'id',
        'sortmode': 'DESC'
    }
    results = core.get_books(url_params=params, is_fiction=False)
    if isinstance(results, int):
        abort(results)
    return jsonify(results)


@app.route('/books/latest/fiction', methods=['GET'])
def get_latest_fiction():
    results = core.get_books(is_fiction=True, is_latest=True)
    if isinstance(results, int):
        abort(results)
    elif len(results['items']) == 0:
        abort(404)
    return jsonify(results)


@app.route('/books/latest/non-fiction', methods=['GET'])
def get_latest_non_fiction():
    results = core.get_books(is_fiction=False, is_latest=True)
    if isinstance(results, int):
        abort(results)
    elif len(results['items']) == 0:
        abort(404)
    return jsonify(results)


if __name__ == '__main__':
    app.run()
