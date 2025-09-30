# services/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Service, Cart, CartItem, Order, OrderItem, Review
from .serializers import ServiceSerializer, CartSerializer, CartItemSerializer, OrderSerializer, ReviewSerializer
from rest_framework import filters
from rest_framework import permissions

from decimal import Decimal
from django.db import transaction
from django.db.models import F

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    # allow sorting by rating: ?ordering=-average_rating
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['average_rating','price','created_at']
    search_fields = ['title','description']

class CartMeView(generics.GenericAPIView):
    """
    GET  /api/v1/cart/      -> return the current user's cart (create if missing)
    POST /api/v1/cart/      -> idempotently ensure a cart exists and return it
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, _created = Cart.objects.get_or_create(user=self.request.user)
        # If you need items preloaded:
        return Cart.objects.select_related('user').prefetch_related('items').get(pk=cart.pk)

    def get(self, request, *args, **kwargs):
        cart = self.get_object()
        return Response(self.get_serializer(cart).data)

    def post(self, request, *args, **kwargs):
        # Idempotent "create": always return the user's cart (create if missing)
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
class CartDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer
    queryset = Cart.objects.select_related('user').prefetch_related('items')
    lookup_field = 'pk'


class CartItemViewSet(viewsets.ModelViewSet):
    """
    list   -> GET   /api/cart/items/
    retrieve -> GET   /api/cart/items/{id}/
    create  -> POST  /api/cart/items/        { "service_id": <int>, "quantity": <int> }
    update  -> PUT   /api/cart/items/{id}/   { "quantity": <int> }
    partial_update -> PATCH /api/cart/items/{id}/ { "quantity": <int> }
    destroy -> DELETE /api/cart/items/{id}/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Only return items from the requesting user's cart
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.select_related('service').filter(cart=cart)
        # Overriding get_queryset per DRF docs is the standard way to filter by user. :contentReference[oaicite:1]{index=1}

    def perform_create(self, serializer):
        # Serializer.create already merges duplicates and uses self.context['request'].user
        serializer.save()

    def perform_update(self, serializer):
        # Only allow quantity to change; service should remain the same for integrity
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        # Ensure the item belongs to the user's cart
        instance = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        # optional: check that user had order with that service and status completed
        serializer.save(user=self.request.user)
