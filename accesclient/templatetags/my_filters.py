from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)

@register.filter
def get_attribute(obj, attr_name):
    try:
        # Replace spaces with underscores in the attribute name
        attr_name = attr_name.replace(' ', '')
        value = getattr(obj, attr_name)
        
        # Format dates
        if isinstance(value, datetime.datetime):
            return timezone.localtime(value).strftime('%d/%m/%Y %H:%M')
        elif isinstance(value, datetime.date):
            return value.strftime('%d/%m/%Y')
            
        return value
    except AttributeError:
        return ''
    
@register.filter
def get_key_or_value(dictionary, key_or_value):
    if key_or_value in dictionary:
        return dictionary[key_or_value]
    else:
        return key_or_value

@register.filter
def is_phone(value):
    """Check if the contact type is a phone number"""
    if not value:
        return False
    value_lower = str(value).lower()
    phone_keywords = ['telephone', 'tel', 'portable', 'mobile', 'phone','fixe']
    return any(keyword in value_lower for keyword in phone_keywords)

@register.filter
def is_email(value):
    """Check if the contact type is an email"""
    if not value:
        return False
    value_lower = str(value).lower()
    email_keywords = ['email', 'mail', 'courriel', 'e-mail']
    return any(keyword in value_lower for keyword in email_keywords)
    return any(keyword in value_lower for keyword in email_keywords)