from apscheduler.schedulers.background import BackgroundScheduler
from .BankNifty import BANKNIFTY
from .Nifty import NIFTY
from .Stock import Stock
from .Stock_Put import Stock_Put


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, id='banknifty_001')
    scheduler.add_job(NIFTY, "interval", minutes=0.27, id='nifty_001',) 
    scheduler.add_job(Stock, "interval", minutes=0.27, id='Stock_001', replace_existing=True)
    scheduler.add_job(Stock_Put, "interval", minutes=0.27, id='Stock_Put_001', replace_existing=True)
                    
    # scheduler.add_job(print_hello, "interval", minutes=0.2, id='printhello_001', replace_existing=True)
    scheduler.start()