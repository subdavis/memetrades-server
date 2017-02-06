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

from mongoengine import DoesNotExist, ValidationError

from . import models
from . import facebookShim

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
            time.sleep(.5)
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
# Template webviews
#

def get_paged_stocks(page):
    page = int(page)
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    return models.Stock.objects(blacklisted=False).only('name','price','trend').skip(offset).limit(settings.STOCKS_PER_PAGE).order_by('-price')

@app.route('/')
def index():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    leaders = models.get_leaders()
    return render_template('index.html',
        base_url=settings.SERVER_NAME,
        leaders=leaders,
        stocks=get_paged_stocks(page),
        page=page)

@app.route('/stock/<stockid>')
def index_stock(stockid):
    try:
        page = int(request.args.get('page')) if request.args.get('page') else 1
        stock = models.Stock.objects.filter(id=stockid).first()
        leaders = models.get_leaders()
        return render_template('index.html',
            base_url=settings.SERVER_NAME,
            leaders=leaders,
            stock=stock,
            stocks=get_paged_stocks(page),
            page=page)
    except DoesNotExist as e:
        return redirect(url_for('index'))
    except ValidationError as e:
        return redirect(url_for('index'))

#
# Private APIs
# 

@app.route('/api/me')
@login_required
def memes():
    return jsonify({
        "money": current_user.money,
        "stocks": current_user.get_holdings(),
        "api_key": current_user.api_key,
        "stock_value": current_user.stock_value
    })

@app.route('/api/buy')
@login_required
def buy():
    meme = request.args.get("meme").strip()
    stock = models.Stock.objects.filter(name=meme).first()
    if not stock:
        stock = models.Stock(name=meme, price=0, history=[])
        stock.save()

    if current_user.buy_one(stock):
        return success()
    return fail()

@app.route('/api/sell')
@login_required
def sell():
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).first()
    if stock:
        if current_user.sell_one(stock):
            return success()
    return fail()

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#
# Admin endpoints
#

@app.route('/api/admin/stock/delete')
@login_required
@requires_roles('admin')
def admin_remove():
    meme = request.args.get("meme")
    if meme:
        stock = models.Stock.objects.filter(name=meme).first()
        if stock:
            stock.blacklist()
            return success()
    return fail()

#
# Publically available APIS
# 

@app.route('/api/stock')
def stock():
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).only('name','price','trend','id').first()
    if stock:
        return Response(stock.to_json(), mimetype="application/json")
    else:
        return jsonify({})

@app.route('/api/leaders')
def leaders():
    return jsonify(models.get_leaders())

@app.route('/login')
def login():
    """ /login is hit before and after the user gets to facebook. """
    callback_base = settings.SERVER_NAME
    if app.config['DEBUG']:
        # bypass auth, just login the local user and go to index
        login_user(get_local_user())
        return redirect(url_for('index'))
    else:
        return facebook.authorize(callback=callback_base + url_for("oauth_authorized"))

@app.route('/oauth-authorized')
@facebook.authorized_handler
def oauth_authorized(resp):
    """Called after the oauth flow is done."""
    next_url = url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)
    user_data = fbshim.get_user(resp['access_token'])
    user = load_user(user_data['user_id'])
    if not user:
        user = models.User()
        user.init(user_data['name'], user_data['user_id'])
        user.save()
    login_user(user)
    logger.info("Welcome, " + user.name)
    redirect_to_client = redirect(url_for('index'), code=302)
    response = app.make_response(redirect_to_client )  
    response.set_cookie('api_key',value=user.api_key)
    return response

@app.route('/api/stocks')
def stocks():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    all_stocks = get_paged_stocks(page)
    return Response(all_stocks.to_json(), mimetype="application/json")

@app.route('/api/history')
def history():
    print(request.url)
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).first()
    ret = []
    if stock:
        for h in stock.history:
            ret.append({
                "price": h.price,
                "time": datetime.datetime.fromtimestamp(h.time)
            })
    return jsonify(ret)

@app.route('/api/recent')
def recent():   
    return jsonify(transactions[-100:])

#
# A few other helpers
#

def success():
    return jsonify({"status":"success"})

def fail():
    return jsonify({"status":"fail"})

def role_error(roles):
    return jsonify({"status": "fail", "reason": "user does not have permission"})
