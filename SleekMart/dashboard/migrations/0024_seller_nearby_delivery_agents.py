# Generated by Django 4.2.5 on 2024-01-21 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0023_deliveryagent_latitude_deliveryagent_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='seller',
            name='nearby_delivery_agents',
            field=models.ManyToManyField(blank=True, to='dashboard.deliveryagent'),
        ),
    ]
