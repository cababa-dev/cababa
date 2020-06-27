import japanmap

from django import template


register = template.Library()

@register.filter(name='prefecture_str')
def prefecture_str(value):
    if value == 0:
        return '非公開'
    return japanmap.pref_names[value]