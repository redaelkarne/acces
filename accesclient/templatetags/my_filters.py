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
        
        # Format dates without timezone conversion (dates are already in local time from DB)
        if isinstance(value, datetime.datetime):
            return value.strftime('%d/%m/%Y %H:%M')
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

@register.filter
def format_local_datetime(value, format_string="d/m/Y H:i"):
    """
    Format a datetime in local timezone.
    Converts from UTC storage to local Paris time for display.
    """
    if not value:
        return ''
    
    if isinstance(value, datetime.datetime):
        # If timezone-aware, convert to local timezone for display
        if timezone.is_aware(value):
            from zoneinfo import ZoneInfo
            local_tz = ZoneInfo('Europe/Paris')
            value = value.astimezone(local_tz)
        
        # Format the datetime
        format_map = {
            'd/m/Y H:i': '%d/%m/%Y %H:%M',
            'd/m/Y': '%d/%m/%Y',
        }
        return value.strftime(format_map.get(format_string, '%d/%m/%Y %H:%M'))
    elif isinstance(value, datetime.date):
        return value.strftime('%d/%m/%Y')
    return str(value)

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()