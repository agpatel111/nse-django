# Generated by Django 4.1.3 on 2022-12-01 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("nse_app", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="profit_margin",
            old_name="percentage",
            new_name="percent",
        ),
    ]
