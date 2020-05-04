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
        'is_approval',
        'created_at',
        'updated_at',
    )


@admin.register(models.LinePayTransaction)
class LinePayTransactionAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'transaction_id',
        'access_token',
        'url',
        'reservation',
        'confirmed',
        'canceled',
        'return_code',
        'return_message',
        'amount',
        'currency',
        'created_at',
        'updated_at',
    )


@admin.register(models.ZoomMeeting)
class ZoomMeetingAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'meeting_id',
        'join_url',
        'start_url',
        'reservation',
        'created_at',
        'updated_at',
    )