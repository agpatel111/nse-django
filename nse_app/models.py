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

option_names = (
    ('NIFTY', 'NIFTY'),
    ('BANKNIFTY', 'BANKNIFTY'),
    )
# Create your models here.


class nse_setting(models.Model):

    option = models.CharField(max_length=50)
    profit_percentage = models.IntegerField()
    loss_percentage = models.IntegerField()
    set_pcr = models.FloatField()
    baseprice_plus = models.IntegerField()
    you_can_buy = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.option
    
    class Meta:
        db_table = 'settings'
    
class AccountCredential(models.Model):
    username = models.CharField(max_length=50)
    apikey = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    t_otp = models.CharField(max_length=50)
    
    class Meta:
        db_table = 'account_credential'

class stock_detail(models.Model):
    
    base_strike_price = models.FloatField(blank=True, null=True)
    live_Strike_price = models.FloatField(blank=True, null=True)
    buy_price = models.FloatField(blank=True, null=True)
    buy_pcr = models.FloatField(blank=True, default = 0, null=True)
    percentage = models.ForeignKey(nse_setting, on_delete=models.CASCADE)
    sell_price = models.FloatField(blank=True, null=True)
    stop_loseprice = models.FloatField(blank=True, null=True)
    live_brid_price = models.FloatField(blank=True, null=True)
    exit_price = models.FloatField(null=True)
    exit_pcr = models.FloatField(blank=True, default = 0, null=True)
    buy_time = models.DateTimeField(auto_now_add= True)
    sell_buy_time = models.DateTimeField( null=True)
    status = models.CharField(max_length=50, choices=Buy_status, default='empty', blank=True)
    final_status = models.CharField(max_length=50, choices=final_status, default='NA', blank=True )
    stock_name = models.CharField(max_length=50, default='NA', blank=True)
    admin_call = models.BooleanField(default=False)
    call_put = models.CharField(max_length=50, blank=True, choices=call_or_put)
    qty = models.IntegerField(blank=True, default=0)
    order_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.percentage,'->', self.buy_price

    class Meta:
        db_table = 'stocks_details'

class pcr_stock_name(models.Model):
    name = models.CharField(max_length = 100)
    pcr = models.FloatField(null=True)
    date = models.DateTimeField(auto_now=True , null=True)

    class Meta:
        db_table = 'pcr_stockName'
    
class live(models.Model):
    live_banknifty = models.BooleanField(default=False)
    live_nifty = models.BooleanField(default=False)
    live_stock_ce = models.BooleanField(default=False)
    live_stock_pe = models.BooleanField(default=False)
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

class stock_for_buy(models.Model):
    stocks_name = models.CharField(max_length = 100)
    call_or_put = models.CharField(max_length=50, blank=True, choices=call_or_put)
    difference_ce_pe = models.IntegerField(blank=True, null=True)
    PE_side_persnt = models.FloatField(blank=True, null=True)
    CE_side_persnt = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'stock_for_buy'

class pcr_values(models.Model):
    option_name = models.CharField(max_length=50, choices=option_names)
    pcr_value = models.FloatField(blank=True, default=0)
    timestamp = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.option_name

    class Meta:
        db_table = 'pcr_values'

class extra_setting(models.Model):
    pcr_isupdating = models.BooleanField(default=False)

    class Meta:
        db_table = 'extra_setting'
        
class BaseZoneBanknifty(models.Model):
    in_basezone = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.FloatField(null=True, blank=True)
    stop_loss_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'BaseZone_Banknifty'
        
class BaseZoneNifty(models.Model):
    in_basezone = models.BooleanField(default=False, null=True, blank=True)
    base_price = models.FloatField(null=True, blank=True)
    stop_loss_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'BaseZone_Nifty'
        
class ResistanceZone_Banknifty(models.Model):
    in_resistance = models.BooleanField(default=False, null=True, blank=True)
    resistance_price = models.FloatField(null=True, blank=True)
    stop_loss_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'ResistanceZone_Banknifty'
        
class ResistanceZone_Nifty(models.Model):
    in_resistance = models.BooleanField(default=False, null=True, blank=True)
    resistance_price = models.FloatField(null=True, blank=True)
    stop_loss_price = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'ResistanceZone_Nifty'
        
class LiveDataBankNifty(models.Model):
    live_price = models.FloatField(null=True, blank=True)
    created_at = models.TimeField(auto_now=True, null=True, blank=True)
    in_basezone = models.BooleanField(default=False, null=True, blank=True)
    in_resistance = models.BooleanField(default=False, null=True, blank=True)
    
    class Meta:
        db_table = 'LiveData_Banknifty'
        
class LiveDataNifty(models.Model):
    live_price = models.FloatField(null=True, blank=True)
    created_at = models.TimeField(auto_now=True, null=True, blank=True)
    in_basezone = models.BooleanField(default=False, null=True, blank=True)
    in_resistance = models.BooleanField(default=False, null=True, blank=True)
    
    class Meta:
        db_table = 'LiveData_Nifty'