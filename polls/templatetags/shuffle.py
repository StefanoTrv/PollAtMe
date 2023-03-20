import random
from django import template
register = template.Library()

@register.filter
def shuffle(value, on):
    if on:
        aux = list(value)[:]
        random.shuffle(aux)
        return aux
    
    return value