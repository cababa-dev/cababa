from django.contrib import admin

from . import models


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'reservation_id',
        'guest',
        'time',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'guest__display_name',
    )