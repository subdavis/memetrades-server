from mongoengine import *
import time
import datetime
from functools import wraps

from . import utils
from . import settings

connect(settings.DATABASE["name"])

# 
# Exception Classes
# 
class BlacklistedException(Exception):
    pass
class NoMoneyException(Exception):
    pass
class ThisMemeNotInPortfolio(Exception):
    pass
class GenericFailException(Exception):
    pass
class CreationSuspendedException(Exception):
    pass

# 
# Model Classes
#
class User(Document):
    fb_id=StringField(required=True, primary_key=True) #Primary 
    holdings=DictField()
    name=StringField(required=True)
    money=FloatField(required=True)
    stock_value = FloatField(require=True)
    api_key=StringField(required=True)
    referral_code=StringField()
    last_banned_ownership=FloatField()
    admin=BooleanField()

    # holdings Example 
    # { 
    #    "stock_id": amount
    # }

    def init(self, name, fb_id):
        self.fb_id = fb_id
        self.name = name
        self.money = settings.INITIAL_MONEY
        self.last_banned_ownership = 0
        self.stock_value = 0
        self.holdings = {}
        self.api_key = utils.get_new_key()
        self.referral_code = utils.get_new_key()
        self.admin = False
        self.save()

    # 
    # API for database updates
    #

    def buy_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the market price
        Step 3: modify the user account totals
        """
        if self.money > stock.price:
            if not stock.blacklisted:
                if str(stock.id) in self.holdings.keys():
                    self.holdings[str(stock.id)] += 1
                else:
                    self.holdings[str(stock.id)] = 1
                if stock.buy_one(self):
                    self.money -= stock.price
                    self.save()
                    return True
                raise GenericFailException("Something else bad happened in user.buy_one")
            raise BlacklistedException("This stock is banned**")
        raise NoMoneyException("You are out of cash...")

    def sell_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the suer account totals
        Step 3: modify the market price
        """
        if str(stock.id) in self.holdings.keys():
            if self.holdings[str(stock.id)] >= 1:
                self.money += stock.price
                self.holdings[str(stock.id)] -= 1
                if stock.sell_one(self):
                    self.save()
                    return True
                raise GenericFailException("Something else bad happened in user.sell_one")
            raise ThisMemeNotInPortfolio("You don't have any more of these...")
        raise ThisMemeNotInPortfolio("You never owned one of these...")

    #
    # Create a new transaction...
    #
    def _queue_transaction(self, stock, action):
        tx = TransactionBacklog().init(stock=stock,
                                            user=self,
                                            action=action)
        return True
    
    def queue_buy(self, stock):
        if stock.price == 0 and not self.can_buy_new():
            raise CreationSuspendedException("You owned a banned** meme, so buying new memes is disabled for 24 hours.")

        if not stock.blacklisted:
            if self.money > stock.price:
                return self._queue_transaction(stock, "buy")
            raise NoMoneyException("You don't have enough money")
        raise BlacklistedException("This stock is banned** from club penguin.")

    def queue_sell(self, stock):
        if self.holdings[str(stock.id)] >= 1:
            return self._queue_transaction(stock, "sell")
        raise ThisMemeNotInPortfolio("You don't have any of this stock...")

    def can_buy_new(self):
        seconds_per_day = 86400
        if time.time() - seconds_per_day >= self.last_banned_ownership:
            return True
        return False

    def get_holdings(self):
        """
        Process this server-side so the client doesn't have to make n requests to resolve each ID
        """
        ret = []
        for key in self.holdings.keys():
            stock = Stock.objects.get(id=key)
            ret.append({
                "name": stock.name, 
                "amount": self.holdings[key],
                "id": key,
                "price": stock.price,
                "trend": stock.trend
            })
        ret = sorted(ret, 
            key=lambda k: k['amount'], 
            reverse=True) 
        return ret

    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.fb_id

    def get_role(self):
        if self.admin:
            return 'admin'
        return 'user'

    def try_referral(self, code):
        referrer = User.objects.filter(referral_code=code).first()
        if referrer:
            referrer.money += settings.MONEY_PER_REFERRAL
            referrer.save()
            return True
        return False

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return self.admin


class Stock(Document):
    name=StringField(required=True)
    price=FloatField(required=True)
    trend=FloatField()
    blacklisted=BooleanField()
    creator=ReferenceField(User)

    def buy_one(self, user):
        if self.blacklisted:
            return False
        self.price += 1
        hist = StockHistoryEntry(
            stock=self, 
            time=time.time(),
            user=user, 
            price=self.price)
        hist.save()
        self.trend = 1.0
        self.blacklisted = False
        self.save()
        return True

    def sell_one(self, user):
        self.price -= 1
        hist = StockHistoryEntry(
            stock=self, 
            time=time.time(), 
            user=user,
            price=self.price)
        hist.save()
        self.trend = -1.0
        self.save()
        return True

    def get_id(self):
        return str(self.id)

    def get_value(self, amount):
        """Get the current evaluation of a stock"""
        if amount > 0:
            total_worth = (self.price * (self.price + 1)) / 2.0
            other_worth = 0
            if amount < self.price:
                # Others own shares...
                not_my_shares = self.price - amount
                other_worth = (not_my_shares*(not_my_shares+1)) / 2.0
            return total_worth - other_worth
        return 0

    def blacklist(self):
        """
        Flag the meme as blacklisted, and don't show on the main page.
        It will continue to show in a shareholder's portfolio, but they cannot buy or sell.
        """
        self.blacklisted = True
        self.save()


class StockHistoryEntry(Document):
    stock=ReferenceField(Stock, required=True)
    user=ReferenceField(User)
    time=FloatField(required=True)
    price=FloatField(required=True)


class TransactionBacklog(Document):
    stock=ReferenceField(Stock, required=True)
    user=ReferenceField(User, required=True)
    action=StringField(required=True)
    time=FloatField(required=True)
    price=FloatField(required=True)

    def init(self, stock=stock, user=user, action="NOOP"):
        self.stock = stock
        self.user = user
        self.action = action
        self.time = time.time()
        self.price = stock.price
        self.save()
        return self

    def process(self):
        if self.action == 'buy':
            self.user.buy_one(self.stock)
        elif self.action == 'sell':
            self.user.sell_one(self.stock)
        
        print("[{time}][{action}] {stock_name} - {user}".format(
            time=round(self.time),
            action=self.action,
            stock_name=self.stock.name[:50].encode('ascii', 'ignore'),
            user=self.user.name.encode('ascii', 'ignore')))


def get_recents():
    result = StockHistoryEntry.objects.order_by('-time').limit(50)
    ret = []
    for r in result:
        s = Stock.objects.get(id=r['stock']['id'])
        ret.append({
            "name":s['name'],
            "price": r['price'],
            "trend":s['trend'],
            "id": str(r['stock']['id'])
        })
    return ret

def get_leaders():
    result = User._get_collection().aggregate([
            {
                '$project' : { 
                    'name': 1, 
                    'fb_id': 1,
                    'total': {'$add': ['$money', '$stock_value'] }
                }
            },
            { '$sort': {'total': -1} },
            { '$limit': 20 }
        ])
    ret = []
    for item in result:
        item['name'] = ''.join(w[0] for w in item['name'].split())
        ret.append(item)
    return ret

def ban_meme(meme_id):
    match_dict = {}
    match_dict['holdings.{meme_id}'.format(meme_id=meme_id)] = { '$gt' : 0 }
    users_owning_meme = User._get_collection().aggregate([
            {
                '$match': match_dict
            }
        ])
    for user in users_owning_meme:
        print(user)
        real_user = User.objects.get(fb_id=user['fb_id'])
        real_user.last_banned_ownership = time.time()
        real_user.save()
    return


def sanity_checks():
    """
    Function for enforcing new database rules on startup...
    """

    # Add Blacklisting
    # stocks = Stock.objects(blacklisted__exists=False)
    # for stock in stocks:
    #     stock.blacklisted = False
    #     stock.save()

    # Add stock_value property
    # users = User.objects(stock_value__exists=False)
    # for user in users:
    #     holdings = user.get_holdings()
    #     user.stock_value = 0.0;
    #     for item in holdings:
    #         user.stock_value += Stock.objects.get(id=item['id']).get_value(item['amount'])
    #     user.save()

    # Turn embedded history into normal fucking documents
    # for s in Stock.objects:
    #     for h in s.history:
    #         newh = StockHistoryEntry(stock=s, time=h.time, price=h.price)
    #         newh.save()
    
    # users = User.objects(referral_code__exists=False)
    # for user in users:
    #     user.referral_code = utils.get_new_key()
    #     user.save()
    
    users = User.objects(last_banned_ownership__exists=False)
    for user in users:
        user.last_banned_ownership = 0
        user.save()

    pass