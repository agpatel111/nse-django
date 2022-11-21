from django.db import models
import uuid


# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(primary_key = True, editable = False, default = uuid.uuid4)

    class Meta:
        abstract = True


class nse_model(BaseModel):
    strike_price = models.FloatField()
    bid_price = models.FloatField()
    buy_time = models.DateTimeField(auto_now = True)
    live_price = models.FloatField()
    pcr_value = models.FloatField()
   

class nse_profit(BaseModel):
    strike_price = models.FloatField()
    bid_price = models.FloatField()
    buy_time = models.DateTimeField(auto_now = True)
    live_price = models.FloatField()
    pcr_value = models.FloatField()
    

class nse_data(BaseModel):
    strike_price = models.FloatField()
    bid_price = models.FloatField()
    buy_time = models.DateTimeField(auto_now = True)
    live_price = models.FloatField()
    pcr_value = models.FloatField()

Buy_status = (
    ('BUY', 'BUY'),
    ('SELL', 'SELL'),
    ('empty', 'empty'),

    )

class nse(BaseModel):
    
    strike_price = models.FloatField()
    bid_price = models.FloatField()
    buy_time = models.DateTimeField(auto_now_add= True)
    live_price = models.FloatField()
    pcr_value = models.FloatField()
    shell_bid_price = models.FloatField(null=True)
    shell_strike_price = models.FloatField(null=True)
    shell_buy_time = models.DateTimeField(auto_now = True, null=True)
    buy_status = models.CharField(max_length=50, choices=Buy_status, default='empty', blank=True)

    

