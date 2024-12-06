from django import template

from flowers.models import Flower

register = template.Library()

@register.filter
def get_item(the_list, item_id):
    try:
        return the_list.get(int(item_id))  # Assumes the_list is a dictionary
    except (AttributeError, KeyError):
        return None

@register.filter
def calculate_subtotal(value1, value2):
    try:
        return value1 * value2
    except TypeError:
        return 0  # Or handle the error appropriately