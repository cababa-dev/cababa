from django.contrib import admin

from . import models


@admin.register(models.OTP)
class OTPAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'otp_id',
        'user',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'user__email',
    )