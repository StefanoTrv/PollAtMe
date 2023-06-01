from django import template
register = template.Library()


"""Template tag for selecting pattern image for each poll"""
@register.filter
def modulo(num, val):
    return num % val