from flask import Flask, request, url_for, jsonify, redirect, Response, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from . import models, settings, app, utils, requires_roles

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
        "stock_value": current_user.stock_value,
        "referral_code": current_user.referral_code
    })

@app.route('/api/buy')
@login_required
def buy():
    models.atomic_lock()
    meme = request.args.get("meme").strip()
    stock = models.Stock.objects.filter(name=meme).first()
    if not stock:
        stock = models.Stock(name=meme, price=0)
        stock.save()

    if current_user.buy_one(stock):
        models.atomic_unlock()
        return utils.success()
    models.atomic_unlock()
    return utils.fail()

@app.route('/api/sell')
@login_required
def sell():
    models.atomic_lock()
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).first()
    if stock:
        if current_user.sell_one(stock):
            models.atomic_unlock()
            return utils.success()
    models.atomic_unlock()
    return utils.fail()

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
            return utils.success()
    return utils.fail()

#
# Publically available APIS
#

@app.route('/api/search')
def search():
    query=request.args.get("q")
    if query:
        stocks= models.Stock.objects.filter(
                name__icontains=query,
                blacklisted=False
            ).only('name','price','trend','id').limit(10)
        return Response(stocks.to_json(), mimetype="application/json")
    return jsonify([])

@app.route('/api/stock')
def stock():
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(
            name=meme,
            blacklisted=False
        ).only('name','price','trend','id').first()
    if stock:
        return Response(stock.to_json(), mimetype="application/json")
    else:
        return jsonify({})

@app.route('/api/leaders')
def leaders():
    return jsonify(models.get_leaders())

@app.route('/api/stocks')
def stocks():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    all_stocks = get_paged_stocks(page)
    return Response(all_stocks.to_json(), mimetype="application/json")

@app.route('/api/history')
def history():
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).first()
    if stock:
        history = models.StockHistoryEntry.objects.filter(stock=stock).order_by('-time').limit(100)
        return Response(history.to_json(), mimetype='application/json')
    return jsonify([])

@app.route('/api/recent')
def recent():   
    # Get the 100 most recent transactions
    # return Response(models.get_recents().to_json(), mimetype='application/json')
    return jsonify(models.get_recents())

#
# Some helpers
#

def get_paged_stocks(page):
    page = int(page)
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    return models.Stock.objects(blacklisted=False).only('name','price','trend').skip(offset).limit(settings.STOCKS_PER_PAGE).order_by('-price')
