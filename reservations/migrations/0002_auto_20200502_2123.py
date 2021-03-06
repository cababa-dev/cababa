# Generated by Django 3.0.5 on 2020-05-02 12:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('reservations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hostess', '0002_auto_20200502_2123'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='guest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='reservation',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hostess.AvailableTime'),
        ),
        migrations.AddField(
            model_name='linepaytransaction',
            name='reservation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reservations.Reservation'),
        ),
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together={('guest', 'time')},
        ),
        migrations.AlterUniqueTogether(
            name='linepaytransaction',
            unique_together={('reservation', 'canceled')},
        ),
    ]
