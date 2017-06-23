MemeTrades.com
==============
![build](https://travis-ci.org/suBDavis/memetrades-server.svg?branch=master)

### On the web...
* [Subreddit](https://reddit.com/r/memetrades)
* or email developers [at] memetrades [dot] com

### Docker production deploy

#### Database
`docker build -f Dockerfile.mongo -t mongo .`
`docker run -d --name mongo mongo`

#### Web
`docker build -f Dockerfile.web -t memes .`
`docker run -dt --link mongo:mongo -p 8080:8080 --name memect memes`

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
7. Run `python process_queue.py`
8. Run `python update.py` every 2 minutes or so. use a cron job or something. IDK, sue me
9. open mongo and type 

```
use memes

db.stock_history_entry.createIndex({"time":1})

db.stock_history_entry.createIndex({"stock":1})

```
what? you don't want to get your hands dirty and mess with mongo? 

You think this could have been automated? You're still mad about the cron job?

I'm tired of getting sass from you. Cash me ousside, How bow dah.

10. Server will be localhost:8080

### Pull requests

we will look at them.  Submit an issue along with the PR so we know what you're doing.


### Maintenance.

restart prod:

sudo systemctl restart memeprod.service

restart dev:

sudo systemctl restart memedev.service

restart nginx:

1. test config: sudo nginx -t
2. restart: sudo service nginx restart

# Unit tests.

from server/ run:

`python -m unittest discover -s tests/`
