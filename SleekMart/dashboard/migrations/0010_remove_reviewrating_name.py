# Generated by Django 4.2.6 on 2023-10-09 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_reviewrating_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewrating',
            name='name',
        ),
    ]
