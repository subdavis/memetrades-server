from mongoengine import *
import time

from . import utils
from . import settings


connect(settings.DATABASE["name"])


class StockHistory(EmbeddedDocument):
    time=FloatField(required=True)
    price=FloatField(required=True)

    def init(self, price):
        self.time = time.time()
        self.price = price


class Stock(Document):
    name=StringField(required=True)
    price=FloatField(required=True)
    history=EmbeddedDocumentListField(StockHistory)

    def buy_one(self):
        self.price += 1
        hist = StockHistory()
        hist.init(self.price)
        self.history.append(hist)
        self.save()

    def sell_one(self):
        self.price -= 1
        hist = StockHistory()
        hist.init(self.price)
        self.history.append(hist)
        self.save()


class User(Document):
    # Flask Login Stuff
    fb_id=StringField(required=True, primary_key=True) #Primary 
    holdings=DictField()
    name=StringField(required=True)
    money=FloatField(required=True)
    api_key=StringField(required=True)

    # holdings Example 
    # { 
    #    "stock_id": number
    # }

    def init(self, name, fb_id):
        self.fb_id = fb_id
        self.name = name
        self.money = settings.INITIAL_MONEY
        self.holdings = {}
        self.api_key = utils.get_new_key()
        self.save()

    # 
    # API for database updates
    #

    def buy_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the market price
        """
        if (self.money > stock.price):
            if stock.name in self.holdings.keys():
                self.holdings[stock.name] += 1
            else:
                self.holdings[stock.name] = 1
            self.money -= stock.price
            stock.buy_one()
            self.save()
            return True
        return False

    def sell_one(self, stock):
        """
        Step 1: modify the user holdings
        Step 2: modify the market price
        """
        if stock.name in self.holdings.keys():
            if self.holdings[stock.name] >= 1:
                self.money += stock.price
                self.holdings[stock.name] -= 1
                stock.sell_one()
                self.save()
            return False
        return False

    def get_id(self):
        """
        Given the primary key for User, return an instance of the subclass implementation
        """
        return self.fb_id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False