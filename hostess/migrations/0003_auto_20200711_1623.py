# Generated by Django 3.0.5 on 2020-07-11 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostess', '0002_auto_20200502_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='availabletime',
            name='end_at',
            field=models.DateTimeField(db_index=True, verbose_name='end_at'),
        ),
        migrations.AlterField(
            model_name='availabletime',
            name='start_at',
            field=models.DateTimeField(db_index=True, verbose_name='start_at'),
        ),
    ]