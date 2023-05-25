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
    print(value)
    if schulze_order != None:
        result = []
        used_fields = []
        for alternative in schulze_order:
          for field in value:
              if "<th><label>"+alternative+":</label></th>" in str(field) and field not in used_fields:
                  result.append(field)
                  used_fields.append(field)
                  break
        return result  
    elif on:
        aux = list(value)[:]
        random.shuffle(aux)
        return aux
    
    return value