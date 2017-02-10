from flask import Flask, request, url_for, jsonify, redirect, Response, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from . import models, settings, app, utils, api_views
from mongoengine import DoesNotExist, ValidationError

#
# Template webviews
#

@app.route('/')
def index():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    leaders = models.get_leaders()
    stocks = api_views.get_paged_stocks(page)
    return render_template('index.html',
        view="market",
        base_url=settings.SERVER_NAME,
        leaders=leaders,
        stocks=stocks,
        page=page,
        stock=stocks.first())

@app.route('/portfolio')
@login_required
def index_portfolio():
    leaders = models.get_leaders()
    stocks = current_user.get_holdings()
    stock = None;
    if len(stocks) >= 1:
        stock = models.Stock.objects.filter(id=stocks[0]['id']).first()
    return render_template('index.html',
        view="portfolio",
        base_url=settings.SERVER_NAME,
        leaders=leaders,
        stocks=stocks,
        stock=stock,
        page=1)

@app.route('/recent')
def index_recent():
    leaders = models.get_leaders()
    stocks = models.get_recents()
    stock = None;
    if len(stocks) >= 1:
        stock = stocks[0]
    return render_template('index.html',
        view="recent",
        base_url=settings.SERVER_NAME,
        leaders=leaders,
        stocks=stocks,
        stock=stock,
        page=1)

@app.route('/stock/<stockid>')
def index_stock(stockid):
    try:
        page = int(request.args.get('page')) if request.args.get('page') else 1
        stock = models.Stock.objects.filter(id=stockid).first()
        leaders = models.get_leaders()
        return render_template('index.html',
            view="market",
            base_url=settings.SERVER_NAME,
            leaders=leaders,
            stock=stock,
            stocks=api_views.get_paged_stocks(page),
            page=page)
    except DoesNotExist as e:
        return redirect(url_for('index'))
    except ValidationError as e:
        return redirect(url_for('index'))