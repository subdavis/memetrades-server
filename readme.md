## Image Branch Notes
- STILL NEED MORE TESTING FOR SIGHTENGINE API'S EFFECTIVENESS
- For some reason the Sightengine POST function I wrote does not count towards the API usage limit (may have something to do with reading the image in binary mode)
  - models.has_nudity_POST()
  - you should use this for testing if possible
- My dev id and secret key for Sightengine API are located in settings-example.py (pls change these if pushing to production)
  - please make your own Sightengine account to dev with, if you want access to the API logs at https://sightengine.com
- Currently only supports image URLs
  - not sure how to do image uploads yet without letting potentially nasty images touch the server
  - also doesn't support imgur links
    - currently using GET request to check if url is an image file or not
      - imgur (and other sites) require auth API for this
- Image changing modeled after buy/sell functionality
  - is a GET request
  - should probably be a POST request, but I got a 405 error and wasn't sure how to work around it
- Image changing limited to once per day
  - modeled after user suspension code
  - this limit (and user suspension length) should probs be moved to settings
- Not sure if I updated requirements.txt correctly
  - most new requirements are in models.py
- Make HTML/CSS prettier
  - image is squished/stretched if not the right dimensions
  - placeholder image is logo-shit.png
  - touch up image change button


MemeTrades.com
==============
![build](https://travis-ci.org/meme-exchange/server.svg?branch=master)

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
7. Run `python process_queue.py`
8. Run `python update.py` every 2 minutes or so. use a cron job or something. IDK, sue me
9. open mongo and type

use memes

db.stock_history_entry.createIndex({"time":1})

db.stock_history_entry.createIndex({"stock":1})

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
