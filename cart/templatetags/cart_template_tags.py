from django import template
from cart.models import Order , OrderItem

register = template.Library()
# @register.inclusion_tag('navbar.html')

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order  = Order.objects.filter(user=user, ordered = False)
        if order.exists():
            return order.count()
    return 0