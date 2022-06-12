from datetime import timedelta
from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)

@register.filter
def duration(dt):
    if dt:
        hours, seconds = divmod((dt.seconds + dt.microseconds * 1000000), 3600)
        minutes, seconds = divmod(seconds, 60)
        hours += dt.days * 24
        return '{0:02}:{1:02}:{2:02}'.format(hours, minutes, seconds)
    else:
        return ""

@register.filter
def diffduration(dt):
    if dt:
        hours, seconds = divmod(abs(int(dt.total_seconds())), 3600)
        minutes, seconds = divmod(seconds, 60)
        if dt.total_seconds() < 0:
            return '-{0:02}:{1:02}:{2:02}'.format(hours, minutes, seconds)
        else:
            return '{0:+03}:{1:02}:{2:02}'.format(hours, minutes, seconds)
    else:
        return ""