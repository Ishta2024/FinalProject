# Generated by Django 4.2.5 on 2024-01-31 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0035_alter_orderitem_delivery_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='delivery_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
    ]