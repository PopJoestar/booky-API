#!/bin/bash

source venv/bin/activate
gunicorn wsgi:app
