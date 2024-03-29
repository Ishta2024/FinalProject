# Generated by Django 4.2.5 on 2024-01-30 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0031_orderitem_delivery_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='delivery_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
    ]
