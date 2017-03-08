import unittest
import env
import time

from memeServer import models


class TestModels(unittest.TestCase):

    def test_recents(self):
        recents = models.get_recents()
        self.assertTrue(len(recents)<=50)
        self.assertTrue(recents != None)

    def test_leaders(self):
        # There should be 1 user, 1 leader
        leaders = models.get_leaders()
        self.assertTrue(len(leaders)==1)

    def test_buy(self):
        some_user = models.User.objects.first()
        some_user.money = 100
        some_user.save()
        self.assertTrue(some_user.money == 100)
        some_stock = models.Stock.objects.first()
        some_stock.price = 50
        some_stock.save()
        self.assertTrue(some_stock.price == 50)
        
        some_user.buy_one(some_stock)
        self.assertTrue(some_user.money == 49) # Currently stock price is incremented first...
        self.assertTrue(some_stock.price == 51)

        # User has no money for another one...
        with self.assertRaises(models.NoMoneyException):
            some_user.buy_one(some_stock)

        self.assertTrue(some_stock.price == 51)
        self.assertTrue(some_user.money == 49)

    def test_sell(self):
        some_user = models.User.objects.first()
        some_user.money = 100
        some_user.save()
        self.assertTrue(some_user.money == 100)
        some_stock = models.Stock.objects.first()
        some_stock.price = 50
        some_stock.save()
        self.assertTrue(some_stock.price == 50)

        some_user.buy_one(some_stock)

        some_user.sell_one(some_stock)
        self.assertTrue(some_user.money == 100)
        self.assertTrue(some_stock.price == 50)

        count_owned = some_user.holdings[str(some_stock.id)]
        if count_owned > 0:
            for i in range(count_owned):
                some_user.sell_one(some_stock)

        with self.assertRaises(models.ThisMemeNotInPortfolio):
            some_user.sell_one(some_stock)

class TestQueueing(unittest.TestCase):

    def test_queue_buy(self):
        some_user = models.User.objects.first()
        some_user.money = 100
        some_user.save()
        some_stock = models.Stock.objects.first()
        some_stock.price = 50
        some_stock.save()

        old_price = some_stock.price
        old_money = some_user.money

        some_user.queue_buy(some_stock)
        time.sleep(.5)

        # Refetch from DB to see new prices
        some_stock = models.Stock.objects.first()
        some_user = models.User.objects.first()
        self.assertTrue(some_stock.price == old_price + 1)
        self.assertTrue(some_user.money == old_money - some_stock.price)

    def test_queue_sell(self):
        self.test_queue_buy() 

        some_stock = models.Stock.objects.first()
        some_user = models.User.objects.first()
        old_price = some_stock.price
        old_money = some_user.money

        some_user.queue_sell(some_stock)

        time.sleep(.5)
        some_stock = models.Stock.objects.first()
        some_user = models.User.objects.first()
        self.assertTrue(some_stock.price == old_price - 1)
        self.assertTrue(some_user.money == old_money + old_price) # account credited with the OLD price
