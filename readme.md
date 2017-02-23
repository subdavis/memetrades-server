MemeTrades.com
==============

### On the web...
* [Subreddit](https://reddit.com/r/memetrades)
* or email developers [at] memetrades [dot] com

### Feature requests or bug reports:

Please open a github issue.  We will read them.  I promise.

### Development setup

Memetrades runs on Ubuntu, and we aren't going to support anything else.

1. Install mongodb `sudo apt install mongodb`
2. Open another terminal and start mongo: `sudo mongod`
3. Create and activate a virtual env for the project
4. Install requirements.txt to the venv.
5. Create a copy of memeServer/settings-example.py as memeServer/settings.py
6. Run `python wsgi.py`
7. Server will be localhost:8080

### Pull requests

we will look at them.  Submit an issue along with the PR so we know what you're doing.
