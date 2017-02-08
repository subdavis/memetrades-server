import memeServer
from memeServer import models
users = models.User.objects()
for user in users:
    holdings = 0
    for key in user.holdings:
        holdings += models.Stock.objects.filter(id=key)[0].get_value(user.holdings[key])
    user.stock_value = holdings
    user.save()
