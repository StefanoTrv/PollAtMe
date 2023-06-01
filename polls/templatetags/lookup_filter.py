from django.template.defaulttags import register

@register.filter
def get_value(dictionary, key):
    """
    Retrieves the value associated with the specified key from a dictionary.

    Args:
        dictionary: The dictionary from which to retrieve the value.
        key: The key whose value is to be retrieved.

    Returns:
        The value associated with the key in the dictionary, or None if the key does not exist.
    """
    return dictionary.get(key)

@register.filter
def replace_space_with_underscore(string):
    """
    Replaces spaces with underscores in the given string.

    Args:
        string: The string in which spaces are to be replaced.

    Returns:
        The modified string with spaces replaced by underscores.
    """
    return string.replace(" ", "_")