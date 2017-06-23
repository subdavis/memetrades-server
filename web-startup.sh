#!/bin/bash
service nginx start
/usr/local/bin/gunicorn --pythonpath /usr/local/lib/ --workers 5 --bind unix:/tmp/meme-prod.sock wsgi:application