# Generated by Django 4.2.5 on 2024-01-15 08:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_alter_deliveryagent_assigned_seller'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('pincode', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='deliveryagent',
            name='assigned_route',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.route'),
        ),
    ]
