# Generated by Django 3.0.5 on 2020-04-26 12:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hostess', '0002_auto_20200426_2104'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('reservation_id', models.UUIDField(db_index=True, default=uuid.uuid4, verbose_name='reservation_id')),
                ('is_approval', models.BooleanField(db_index=True, verbose_name='is_approval')),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostess.AvailableTime')),
            ],
            options={
                'unique_together': {('guest', 'time')},
            },
        ),
    ]
