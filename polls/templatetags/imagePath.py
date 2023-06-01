from django import template
register = template.Library()

@register.filter
def imagePath(num, val):

    id = num % val

    return 'img/patterns/pattern' + str(id) + '.png'