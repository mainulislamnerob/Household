from shop.models import Product
from rest_framework import serializers
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        # ref_name = 'Product'
        model = Product
        fields = ['id', 'name', 'description', 'price', 'product_image', 'created_at', 'updated_at']