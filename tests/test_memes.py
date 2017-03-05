import unittest
import env

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
