# Generated by Django 3.0.5 on 2020-07-11 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0002_auto_20200502_2123'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together=set(),
        ),
    ]
