# Generated by Django 3.0.5 on 2020-06-27 13:42

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20200627_2214'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostessprofile',
            name='name',
            field=models.CharField(default=None, max_length=100, null=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='hostessprofile',
            name='area',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(choices=[('kabukicho', '歌舞伎町'), ('roppongi', '六本木'), ('ginza', '銀座'), ('shibuya', '渋谷'), ('ikebukuro', '池袋'), ('ueno', '上野'), ('kitashinchi', '北新地'), ('minami', 'ミナミ'), ('nakasu', '中州'), ('kokubuncho', '国分町'), ('susukino', 'ススキノ'), ('other', 'その他')], max_length=20), blank=True, db_index=True, default=list, size=10),
        ),
    ]
