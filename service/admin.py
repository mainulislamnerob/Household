from django.contrib import admin
from service.models import Service, Review, Cart, CartItem, Order, OrderItem
# Register your models here.
admin.site.register(Service)
admin.site.register(Review)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)