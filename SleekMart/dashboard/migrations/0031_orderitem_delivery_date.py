# Generated by Django 4.2.5 on 2024-01-30 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_order_delivery_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
