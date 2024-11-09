from django import template
from datetime import datetime, timedelta, date

register = template.Library()

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr, None)

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    if arg != 0:
        return value / arg
    return 0

@register.filter
def filter_by_attr(items, attr):
    """Filter a list of items by checking if they have a non-None/non-False attribute value."""
    return [item for item in items if getattr(item, attr, None)]

@register.filter
def count_by_attr(items, attr):
    """Count items in a list that have a non-None/non-False attribute value."""
    return len([item for item in items if getattr(item, attr, None)])

@register.filter
def sum_attr(items, attr):
    """Sum the values of a specific attribute across all items in a list."""
    return sum(getattr(item, attr, 0) for item in items)


@register.filter
def is_more_than_a_month_old(date_value):
    if date_value is None:  
        return True  # or False, depending on your desired behavior
    one_month_ago = date.today() - timedelta(days=30)  # <--- Changed to date.today()
    return date_value < one_month_ago