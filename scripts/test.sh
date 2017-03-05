#!/bin/bash
mv memeServer/settings-example.py memeServer/settings.py
python -m unittest discover -s tests