# Generated by Django 4.2.5 on 2024-01-15 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_notification_delivery_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryagent',
            name='assigned_seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.seller'),
        ),
    ]