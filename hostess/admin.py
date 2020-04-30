from django.contrib import admin

from . import models


@admin.register(models.AvailableTime)
class AvailableTimeAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'available_id',
        'hostess',
        'start_at',
        'end_at',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'hostess__display_name',
    )