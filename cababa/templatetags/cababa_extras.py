import datetime
import japanmap

from django import template
from django.utils.html import format_html

from lib.date import get_display_dt
from users.models import HostessProfile


register = template.Library()

@register.filter(name='prefecture_str')
def prefecture_str(value):
    if value == 0:
        return '非公開'
    if type(value) != int:
        return '非公開'
    return japanmap.pref_names[value]

@register.filter
def absolute_url(path, request):
    return request.build_absolute_uri(path)

@register.filter(name='get_area_display')
def get_area_display(area):
    for choice in HostessProfile.AreaTypes.choices:
        if choice[0] == area:
            return choice[1]
    return None

@register.filter(name='get_date')
def get_date(dt):
    return get_display_dt(dt)

@register.filter(name='get_style_display')
def get_style_display(style):
    for choice in HostessProfile.StyleTypes.choices:
        if choice[0] == style:
            return choice[1]
    return None

@register.filter(name='line_break')
def line_break(message):
    return format_html('<br/>'.join(message.split('\n')))

@register.filter
def to_https(value):
    return value.replace("http", "https")