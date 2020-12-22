from django.contrib import admin
from .models import Order, OrderItem , Address , Coupon , Refunds

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['user','ordered','being_delivered','received','refund_requested','refund_granted']


admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(Coupon)
admin.site.register(Refunds)
