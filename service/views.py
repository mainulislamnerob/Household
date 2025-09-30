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
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from sslcommerz_lib import SSLCOMMERZ 
from django.conf import settings as main_settings

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Read-only for unauthenticated users
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

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all().order_by('-created_at')

    def get_queryset(self):
        return (Order.objects
                .filter(user=self.request.user)
                .prefetch_related('items__service'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create order + items
        self.perform_create(serializer)

        # re-fetch with prefetch so 'items' serialize properly
        order = (Order.objects
                 .prefetch_related('items__service')
                 .get(pk=serializer.instance.pk))

        out = OrderSerializer(order).data
        headers = self.get_success_headers(out)
        return Response(out, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        with transaction.atomic():
            cart = get_object_or_404(Cart, user=self.request.user)
            cart_items_qs = CartItem.objects.select_related('service').filter(cart=cart)
            cart_items = list(cart_items_qs)
            if not cart_items:
                raise serializers.ValidationError("Cart is empty")

            from decimal import Decimal
            total_amount = sum((ci.service.price * ci.quantity) for ci in cart_items)
            total_amount = Decimal(total_amount)

            order = serializer.save(user=self.request.user, total_amount=total_amount)

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    service=ci.service,
                    service_title=ci.service.title,
                    unit_price=ci.service.price,
                    quantity=ci.quantity,
                    subtotal=ci.service.price * ci.quantity
                ) for ci in cart_items
            ])

            CartItem.objects.filter(id__in=[ci.id for ci in cart_items]).delete()
class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        # optional: check that user had order with that service and status completed
        serializer.save(user=self.request.user)

# payment all views

@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = 100
    order_id = request.data.get("order_id")
    num_items = request.data.get("num_items", 1)

    settings = {'store_id': 'phima67ddc8dba290b',
                'store_pass': 'phima67ddc8dba290b@ssl', 'issandbox': True}
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = f"txn_{order_id}"
    post_body['success_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/success/"
    post_body['fail_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/fail/"
    post_body['cancel_url'] = f"{main_settings.BACKEND_URL}/api/v1/payment/cancel/"
    post_body['emi_option'] = 0
    post_body['cus_name'] = f"{user.first_name} {user.last_name}"
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user.phone_number
    post_body['cus_add1'] = user.address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "Courier"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = num_items
    post_body['product_name'] = "E-commerce Products"
    post_body['product_category'] = "General"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body)  # API response

    if response.get("status") == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']})
    return Response({"error": "Payment initiation failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def payment_success(request):
    print("Inside success")
    order_id = request.data.get("tran_id").split('_')[1]
    order = Order.objects.get(id=order_id)
    order.status = "CONFIRMED"
    order.save()
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/ordered/")


@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/ordered/")


@api_view(['POST'])
def payment_fail(request):
    print("Inside fail")
    return HttpResponseRedirect(f"{main_settings.FRONTEND_URL}/dashboard/ordered/")