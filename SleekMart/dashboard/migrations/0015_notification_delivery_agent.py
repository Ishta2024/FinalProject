# Generated by Django 4.2.5 on 2024-01-15 06:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='delivery_agent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboard.deliveryagent'),
        ),
    ]
