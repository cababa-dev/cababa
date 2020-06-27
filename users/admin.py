from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.utils.html import format_html, escape

from . import models


# Define a new User admin
admin.site.register(models.User, BaseUserAdmin)

# Re-register GroupAdmin
admin.site.unregister(Group)
# Define a new Group admin
admin.site.register(models.Group, BaseGroupAdmin)

@admin.register(models.HostessProfile)
class HostessProfileAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'hostess',
        'name',
        'image_tag',
        'height',
        'prefecture_code',
        'area',
        'body',
        'age',
        'style',
        'personality',
        'message',
        'rank',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'hostess__display_name',
    )
    def image_tag(self, obj):
        return format_html('<img src={} width=50, height=50 />'.format(escape(obj.images[0])))
    image_tag.short_description = "image"
    image_tag.allow_tags = True


@admin.register(models.GuestProfile)
class GuestProfileAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'guest',
        'prefecture_code',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'guest__display_name',
    )


@admin.register(models.TagGroup)
class TagGroupAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'name',
        'title',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'name',
        'title',
    )

@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    date_heirarchy = (
        'updated_at',
    )
    list_display = (
        'group',
        'value',
        'name',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'name',
        'value',
    )