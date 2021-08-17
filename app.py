from falcon import App
from resources import Fiction, NonFiction


app = App()


fiction = Fiction()
non_fiction = NonFiction()


app.add_route('/books/fiction', fiction)
app.add_route('/books/fiction/latest', fiction, suffix='latest')
app.add_route('/books/fiction/details/{md5}', fiction, suffix='details')

app.add_route('/books/non-fiction', non_fiction)
app.add_route('/books/non-fiction/latest', non_fiction, suffix='latest')
app.add_route(
    '/books/non-fiction/details/{md5}', non_fiction, suffix='details')
