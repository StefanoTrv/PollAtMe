from django.template.defaulttags import register

@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)
@register.filter
def replace_space_with_underscore(string):
    return string.replace(" ", "_")

@register.filter
def tokens_status(object_list, used):
    return object_list.filter(used=used)