import memeServer
import time
from memeServer import models

# This code handles queue processing in a single thread....
# Is it good?  No.
# Is it better than before?  Honestly IDK.  It works tho.

while True:
    transactions = models.TransactionBacklog.objects().order_by('time')
    for t in transactions:
        try: 
            t.process()
        except Exception as e:
            print("* transaction failed:" + str(e))
        t.delete()
    time.sleep(.1)
#except Exception as e:
#    print("-------------------------")
#    print("EXCEPTION: Something BAD happened...")
#    print(e)
#    print("-------------------------")
