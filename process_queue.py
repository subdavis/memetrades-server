import memeServer
import time
from memeServer import models

while True:
    
    transactions = models.TransactionBacklog.objects().order_by('time')
    
    for t in transactions:
        t.process()
    for t in transactions:
        t.delete()
    
    time.sleep(.1)