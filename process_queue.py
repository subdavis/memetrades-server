import memeServer
import time
from memeServer import models

# This code handles queue processing in a single thread....
# Is it good?  No.
# Is it better than before?  Honestly IDK.  It works tho.

while True:
    
    try:
        transactions = models.TransactionBacklog.objects().order_by('time')
        
        for t in transactions:
            t.process()
        for t in transactions:
            t.delete()
        
        time.sleep(.1)
    
    except Exception as e:
        print("---- EXCEPTION ----")
        print(e)
        print("-------------------")