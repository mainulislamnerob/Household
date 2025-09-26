from rest_framework import serializers
from .models import Service, CartItem, Cart, Order, OrderItem, Review

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Service.objects.all(), source='service')
    class Meta:
        model = CartItem
        fields = ('id','service','service_id','quantity','added_at')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ('id','user','items','created_at')
        read_only_fields = ('user',)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('service_title','unit_price','quantity','subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id','user','status','created_at','total_amount','payment_status','items')
        read_only_fields = ('user','total_amount','created_at')

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Review
        fields = ('id','service','user','order','rating','comment','created_at')