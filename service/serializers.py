from rest_framework import serializers
from .models import Service, CartItem, Cart, Order, OrderItem, Review
from rest_framework import serializers
from .models import Cart
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at']  # adjust as needed
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        # Defensive: make sure the request user is set, not taken from client input
        request = self.context.get('request')
        return Cart.objects.get_or_create(user=request.user)[0]

class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Service.objects.all(), source='service')
    cart_id = serializers.PrimaryKeyRelatedField(write_only=True, queryset=Cart.objects.all(), source='cart')

    class Meta:
        model = CartItem
        fields = ('id','service','service_id','cart_id','quantity','added_at')


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('service_title','unit_price','quantity','subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ('id','user','status','created_at','total_amount','payment_status','items')
        read_only_fields = ('user','created_at')

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Review
        fields = ('id','service','user','order','rating','comment','created_at')