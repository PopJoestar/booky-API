from multiprocessing import cpu_count

bind = '127.0.0.1:8000'

workers = cpu_count() * 2 + 1
worker_class = 'gevent'
worker_connections = 100
timeout = 30
debug = False
reload = True
