from django.template.defaulttags import register

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)
@register.filter
def replace_space_with_underscore(string):
    return string.replace(" ", "_")