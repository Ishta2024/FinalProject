# Generated by Django 4.2.5 on 2024-01-25 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0025_deliveryagent_distance'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='pincode',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]