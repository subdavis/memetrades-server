#!/bin/bash
mongorestore --db memes-tests dump/memes
cp memeServer/settings-example.py memeServer/settings.py
python -m unittest discover -s tests