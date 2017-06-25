#!/bin/bash
service nginx start
python process_queue.py &
/usr/local/bin/gunicorn --pythonpath /usr/local/lib/ --workers 5 --bind unix:/tmp/meme-prod.sock wsgi:application