import random
from django import template
register = template.Library()

"""
Three version of shuffle, as a workaround for the fact that you can't have a tag with more than one parameter.
If a schulze_order is provided, the fields are reordered in that order.
Otherwhise, if "on" is True, it randomizes the order of the fields; if "on" is False, it returns the fields without changing their order.
"""

@register.filter
def shuffle(value, on):
    # Calls the shuffle2 function with the value and on parameters, and schulze_order set to None
    return shuffle2((value,on),None)

@register.filter
def shuffle1(value, on):
    # Simply returns the value and on parameters
    return value, on

@register.filter
def shuffle2(value_on, schulze_order=None):
    # Unpacking the value_on tuple into value and on variables
    value, on = value_on
    if schulze_order != None:
        result = []
        used_fields = []
        for alternative in schulze_order:
          for field in value:
            # Checks if the field is about that alternative and if the field has not been used before
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