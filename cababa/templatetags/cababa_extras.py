import japanmap

from django import template


register = template.Library()

@register.filter(name='prefecture_str')
def prefecture_str(value):
    if value == 0:
        return '非公開'
    return japanmap.pref_names[value]

@register.filter
def absolute_url(path, request):
    return request.build_absolute_uri(path)