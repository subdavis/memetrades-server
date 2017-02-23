import memeServer
import time
import schedule
from memeServer import models
from multiprocessing import Process

# 
# Spin up the scheduled jobs...
# 

def calculate_user_holdings():
    """
    job for checking user holdings.
    """
    print("* running calculate_user_holdings...")
    users = models.User.objects()
    for user in users:
        holdings = 0
        for key in user.holdings:
            holdings += models.Stock.objects.filter(id=key)[0].get_value(user.holdings[key])
        user.stock_value = holdings
        user.save()

def job_runner():
    print("* Starting the job runner...")
    while True:
        schedule.run_pending()
        time.sleep(1)

# This code handles queue processing in a single thread....
# Is it good?  No.
# Is it better than before?  Honestly IDK.  It works tho.

def process_queue():
    while True:
        try:
            transactions = models.TransactionBacklog.objects().order_by('time')
            for t in transactions:
                try: 
                    t.process()
                except Exception as e:
                    print("* transaction failed:" + e)
                t.delete()
            time.sleep(.1)
        except Exception as e:
            print("-------------------------")
            print("EXCEPTION: Something BAD happened...")
            print(e)
            print("-------------------------")

if __name__ == '__main__':
    queueProcessor = Process(target=process_queue)
    queueProcessor.start()

    jobRunner = Process(target=job_runner)
    jobRunner.start()

    queueProcessor.join()
    jobRunner.join()