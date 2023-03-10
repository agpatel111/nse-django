# Generated by Django 4.1.5 on 2023-01-19 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0003_stock_detail_buy_pcr_stock_detail_exit_pcr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='live',
            name='banknifty_at_set_pcr',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='live',
            name='banknifty_live_pcr',
            field=models.FloatField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='live',
            name='nifty_at_set_pcr',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='live',
            name='nifty_live_pcr',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
