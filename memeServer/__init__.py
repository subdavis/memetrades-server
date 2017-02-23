from flask import Flask, request, url_for, jsonify, redirect, Response, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from flask_oauth import OAuth
import random
import logging
import pickle
from functools import wraps
import datetime
import re
import time

from . import models
from . import facebookShim

from mongoengine import DoesNotExist, ValidationError

#
# Setup
#

logger = logging.getLogger(__name__)
models.sanity_checks()

#
# App init
#

app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = settings.SECRET_KEY
CORS(app)
logger.info("Running with debug = " + str(app.config['DEBUG']))

#
# Login init
#

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
logger.info("Initialized logins...")

#
# Oauth Handlers and Login
#

fbshim = facebookShim.FacebookShim()
oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=settings.FACEBOOK['APP_ID'],
    consumer_secret=settings.FACEBOOK['APP_SECRET'],
    request_token_params={'scope': 'email'}
)

@login_manager.user_loader
def load_user(fb_id):
    try:
        return models.User.objects.get(fb_id=fb_id)
    except DoesNotExist:
        return None

@login_manager.request_loader
def load_user_from_request(request):
    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = models.User.objects(api_key=api_key).first()
        if user:
            return user
        return None
    return None

# If local debug, bypass fb auth and assume the user is authenticated...
def get_local_user():
    name = "LocalUser"
    user = models.User.objects.filter(name=name).first()
    if not user:
        user = models.User()
        user.init(name, '0')
        user.save()
    return user

# Wrapper for checking user permissions
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.get_role() not in roles:
                return role_error(roles)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

#
# Facebook Login Handlers
#

@app.route('/login')
def login():
    """ /login is hit before and after the user gets to facebook. """
    referral = request.args.get('r')
    state = referral if referral else "NONE"
    callback_base = settings.SERVER_NAME
    if app.config['DEBUG']:
        # bypass auth, just login the local user and go to index
        login_user(get_local_user())
        return redirect(url_for('index'))
    else:
        return facebook.authorize(callback=callback_base + url_for("oauth_authorized") + "?state=" + state)

@app.route('/oauth-authorized')
@facebook.authorized_handler
def oauth_authorized(resp):
    """Called after the oauth flow is done."""
    next_url = url_for('index')
    if resp is None:
        return redirect(next_url)
    user_data = fbshim.get_user(resp['access_token'])
    user = load_user(user_data['user_id'])
    if not user:  
        user = models.User()
        user.init(user_data['name'], user_data['user_id'])
        # Check for referral..
        state = request.args.get('state')
        if state != "NONE":
            print("Referral for " + user.name.encode('ascii', 'ignore'))
            user.money += settings.MONEY_PER_REFERRAL
            user.try_referral(state)
        user.save()
    
    login_user(user)
    # logger.info("Welcome, " + user.name)
    redirect_to_client = redirect(url_for('index'), code=302)
    response = app.make_response(redirect_to_client )  
    response.set_cookie('api_key',value=user.api_key)
    return response

from . import web_views
from . import api_views
