#!/bin/bash
mongorestore --db memes-tests dump/memes
cp memeServer/settings-example.py memeServer/settings.py
python process_queue.py & echo "Spun up background process_queue"
python -m unittest discover -s tests
kill %1 && echo "Joined background process_queue"