from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)
@register.filter
def get_attribute(obj, attr_name):
    try:
        # Replace spaces with underscores in the attribute name
        attr_name = attr_name.replace(' ', '')
        return getattr(obj, attr_name)
    except AttributeError:
        return ''
    
@register.filter
def get_key_or_value(dictionary, key_or_value):
    if key_or_value in dictionary:
        return dictionary[key_or_value]
    else:
        return key_or_value