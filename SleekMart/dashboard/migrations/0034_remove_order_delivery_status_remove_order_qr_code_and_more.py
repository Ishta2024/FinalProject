# Generated by Django 4.2.5 on 2024-01-31 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0033_remove_orderitem_delivery_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='delivery_status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='qr_code',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='delivery_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
    ]