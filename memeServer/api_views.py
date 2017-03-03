from flask import Flask, request, url_for, jsonify, redirect, Response, render_template
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from . import models, settings, app, utils, requires_roles, load_user
import time
import json
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
    meme = request.args.get("meme").strip()
    stock = models.Stock.objects.filter(name=meme).first()
    if not stock:
        stock = models.Stock(name=meme, creator=load_user(current_user.fb_id), price=0)
        stock.save()
    try:
        current_user.queue_buy(stock)
        return utils.success()
    except Exception as e:
        return utils.fail(reason=str(e))

@app.route('/api/sell')
@login_required
def sell():
    meme = request.args.get("meme")
    stock = models.Stock.objects.filter(name=meme).first()
    
    if stock:
        try:
            current_user.queue_sell(stock)
            return utils.success()
        except Exception as e:
            return utils.fail(reason=str(e))
    return utils.fail(reason="Stock does not exist")

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
            if not stock.blacklisted:
                stock.blacklist()
                models.ban_meme(stock.id)
                return utils.success()
            return utils.fail(reason="stock already blacklisted...")
        return utils.fail(reason="the stock did not exist...")
    return utils.fail(reason="the stock did not exist...")

#
# Publically available APIS
#
trending_cache=""
trending_timestamp=-100000
@app.route('/api/trending')
def trends():    
    global trending_timestamp
    global trending_cache
    if time.time() < trending_timestamp + 90*settings.LAG_ALLOWED:
	print "cached"
	return trending_cache
    trending_timestamp = time.time() 
    results = models.get_trending()
    trending_cache = jsonify(results)
    
    return trending_cache

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

stocks_cache={}
stocks_timestamp={}
@app.route('/api/stocks')
def stocks():
    page = int(request.args.get('page')) if request.args.get('page') else 1

    # if the cache is fresh
    if (page in stocks_timestamp) and (stocks_timestamp[page]  > time.time() - settings.LAG_ALLOWED):    
        return stocks_cache[page]
    
    # if the cache is stale
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    all_stocks = get_paged_stocks(page)
    stocks_cache[page] = Response(all_stocks.to_json(), mimetype="application/json")
    stocks_timestamp[page] = time.time()
    return stocks_cache[page]

history_cache = {}
history_timestamp = {}
@app.route('/api/history')
def history():
    meme = request.args.get("meme")

    if (meme in history_timestamp) and (history_timestamp[meme] > time.time() - settings.LAG_ALLOWED * 3):
        return history_cache[meme]

    stock = models.Stock.objects.filter(name=meme).first()
    if stock:
        history = models.StockHistoryEntry.objects.filter(stock=stock).order_by('-time').limit(400)
        history_cache[meme] = Response(history.to_json(), mimetype='application/json')
    else:
        history_cache[meme] = jsonify([])

    history_timestamp[meme] = time.time()
    return history_cache[meme]

recent_cache = ""
recent_timestamp = -10000
@app.route('/api/recent')
def recent():
    global recent_timestamp
    global recent_cache
    if time.time() < recent_timestamp + settings.LAG_ALLOWED:
	print "cached"
	return recent_cache
    
    # Get the 100 most recent transactions
    # return Response(models.get_recents().to_json(), mimetype='application/json')
    recent_cache = jsonify(models.get_recents())
    recent_timestamp = time.time()
    return recent_cache

#
# SMTP Receiver endpoints....
#

@app.route('/email/inbound', methods=['POST','GET'])
def inboud():
    if request.method == 'POST':
        try:
            number_success = 0
            number_fail = 0
            data = json.loads(request.data)
            # data should be a list.
            if len(data) > 0:
                for email in data:
                    # print(email)
                    msg_from = email['msys']['relay_message']['msg_from']
                    from_domain = msg_from.split('@')
                    if len(from_domain) == 2:
                        from_domain = from_domain[1]
                    else:
                        from_domain = "unknown.com"
                    
                    rcpt_to = email['msys']['relay_message']['rcpt_to']
                    # header_from = email['msys']['relay_message']['content']['headers']['From']
                    # header_to = email['msys']['relay_message']['content']['headers']['To'] #this one is a list.
                    subject = email['msys']['relay_message']['content']['subject']
                    webhook_id = email['msys']['relay_message']['webhook_id']
                    user_fb_id = rcpt_to.split('@')[0]
                    user = load_user(user_fb_id)

                    print(rcpt_to, subject, user_fb_id, msg_from)
                    # See if the email matches what we expect..
                    if user and (webhook_id == settings.WEBHOOK_ID):
                        if from_domain in settings.CHARITY_DATA['from']:
                            if subject in settings.CHARITY_DATA['subject']:
                                print("MAIL RECEIPT YES FOR " + user.name)
                                user.money += 1000

                                #store the record for later...
                                if user.donation_count:
                                    user.donation_count += 1
                                    if user.donation_count > 30:
                                        user.donation_replies.append("You've done this too many times")
                                        number_fail += 1
                                        continue
                                else:
                                    user.donation_count = 1
                                if user.donation_replies:
                                    user.donation_replies.append(email['msys']['relay_message']['content']['text'])
                                else:
                                    user.donation_replies = [email['msys']['relay_message']['content']['text']]

                                user.save()
                                number_success += 1
                            else:
                                number_fail += 1
                        else:
                            number_fail += 1
                    else:
                        number_fail += 1
            if number_fail > 0:
                print("MAIL RECEIPT INVALID")
                return utils.fail(reason="unknown")
            return utils.success()
        
        except Exception as e:
            print("EXCEPTION")
            print(str(e))
            return utils.fail(reason="An exception was thrown")
    else:
        return utils.success()

#
# Some helpers
#

def get_paged_stocks(page):
    page = int(page)
    offset = (page - 1) * settings.STOCKS_PER_PAGE
    return models.Stock.objects(blacklisted=False).only('name','price','trend').skip(offset).limit(settings.STOCKS_PER_PAGE).order_by('-price')
