# Generated by Django 4.2.4 on 2023-09-23 04:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alter_reviewrating_rating'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
