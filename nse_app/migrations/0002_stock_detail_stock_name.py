# Generated by Django 4.1.5 on 2023-01-09 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nse_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock_detail',
            name='stock_name',
            field=models.CharField(blank=True, default='NA', max_length=50),
        ),
    ]
