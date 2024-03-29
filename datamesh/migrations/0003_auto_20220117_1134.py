# Generated by Django 2.2.13 on 2022-01-25 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamesh', '0002_auto_20190918_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='origin_lookup_field_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='related_lookup_field_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='origin_fk_field_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='related_fk_field_name',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
