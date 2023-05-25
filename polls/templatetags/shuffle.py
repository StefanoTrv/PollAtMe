import random
from django import template
register = template.Library()

@register.filter
def shuffle(value, on):
    return shuffle2((value,on),None)

@register.filter
def shuffle1(value, on):
    return value, on

@register.filter
def shuffle2(value_on, schulze_order=None):
    value, on = value_on
    if schulze_order != None:
        result = []
        for alternative in schulze_order:
          for field in value:
              if "<th><label>"+alternative+":</label></th>" in str(field):
                  result.append(field)
                  break
        return result  
    elif on:
        aux = list(value)[:]
        random.shuffle(aux)
        return aux
    
    return value