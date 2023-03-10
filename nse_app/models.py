from django.db import models
from django.utils.translation import gettext_lazy as _


Buy_status = (
    ('BUY', 'BUY'),
    ('SELL', 'SELL'),
    ('empty', 'empty'),
    )

final_status = (
    ('PROFIT', 'PROFIT'),
    ('LOSS', 'LOSS'),
    ('NA', 'NA'),
    )

call_or_put = (
    ('CALL', 'CALL'),
    ('PUT', 'PUT'),
    ('NA', 'NA'),
    )

# Create your models here.


class nse_setting(models.Model):

    option = models.CharField(max_length=50)
    profit_percentage = models.IntegerField()
    loss_percentage = models.IntegerField()
    set_pcr = models.FloatField()
    baseprice_plus = models.IntegerField()

    def __str__(self):
        return self.option
    
    class Meta:
        db_table = 'settings'

class stock_detail(models.Model):
    
    base_strike_price = models.FloatField()
    live_Strike_price = models.FloatField()
    buy_price = models.FloatField()
    buy_pcr = models.FloatField(blank=True, default = 0)
    percentage = models.ForeignKey(nse_setting, on_delete=models.CASCADE)
    sell_price = models.FloatField()
    stop_loseprice = models.FloatField()
    live_brid_price = models.FloatField()
    exit_price = models.FloatField(null=True)
    exit_pcr = models.FloatField(blank=True, default = 0)
    buy_time = models.DateTimeField(auto_now_add= True)
    sell_buy_time = models.DateTimeField( null=True)
    status = models.CharField(max_length=50, choices=Buy_status, default='empty', blank=True)
    final_status = models.CharField(max_length=50, choices=final_status, default='NA', blank=True )
    stock_name = models.CharField(max_length=50, default='NA', blank=True)
    admin_call = models.BooleanField(default=False)
    call_put = models.CharField(max_length=50, blank=True, choices=call_or_put)
    qnty = models.IntegerField(blank=True, default=0)
    net_p_l = models.FloatField(blank=True, default=0)

    def __str__(self):
        return self.percentage,'->', self.buy_price

    class Meta:
        db_table = 'stocks_details'
    
    # @classmethod
    # def create(cls, percentage):
    #     percentage = cls(percentage=percentage)
    #     print('hello', percentage)
    #     # do something with the book
    #     return book


class pcr_stock_name(models.Model):
    name = models.CharField(max_length = 100)
    pcr = models.FloatField(null=True)
    date = models.DateTimeField(auto_now=True , null=True)

    class Meta:
        db_table = 'pcr_stockName'
    
class live(models.Model):
    live_banknifty = models.BooleanField(default=False)
    live_nifty = models.BooleanField(default=False)
    live_stock = models.BooleanField(default=False)
    live_set = models.BooleanField(default=False)

    class Meta:
        db_table = 'live_settings'
    
class pcr_option(models.Model):

    OptionName = models.CharField(max_length=50)
    AtSetPcr = models.BooleanField(blank=True,null=True, default=False)
    PcrStopLoss = models.FloatField(blank=True,null=True)
    LivePcr = models.FloatField(blank=True, default=0)
    
    class Meta:
        db_table = 'pcr_options'
