# Generated by Django 4.2.5 on 2024-01-25 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0028_remove_order_delivery_agent_orderitem_delivery_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='qr_codes/'),
        ),
    ]