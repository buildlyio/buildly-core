# Generated by Django 2.2.10 on 2021-02-17 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200303_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='coreuser',
            name='email_alert_flag',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
