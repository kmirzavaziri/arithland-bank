import math

from django import template

register = template.Library()


@register.filter
def format_hhmmss(t: int) -> str:
    h = math.floor((t / 60) / 60)
    m = math.floor((t / 60) % 60)
    s = t % 60

    return f'{h}:{m:02}:{s:02}'
