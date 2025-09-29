# services/views.py
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Service, Cart, CartItem, Order, OrderItem, Review
from .serializers import ServiceSerializer, CartSerializer, CartItemSerializer, OrderSerializer, ReviewSerializer
from rest_framework import filters
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('-id')
    serializer_class = ServiceSerializer
    # allow sorting by rating: ?ordering=-average_rating
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['average_rating','price','created_at']
    search_fields = ['title','description']

class CartView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__cart').filter(user=self.request.user)
    

class AddToCartAPIView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # if exists, update quantity
        service = serializer.validated_data['service']
        qty = serializer.validated_data.get('quantity',1)
        obj, created = CartItem.objects.get_or_create(cart=cart, service=service, defaults={'quantity':qty})
        if not created:
            obj.quantity += qty
            obj.save()
        # return object via serializer in response
    def create(self, request, *args, **kwargs):
        self.perform_create(self.get_serializer(data=request.data))
        return Response({'detail':'added'}, status=status.HTTP_201_CREATED)

class RemoveFromCartAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer
    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        service_id = request.data.get('service_id')
        item = get_object_or_404(CartItem, cart=cart, service_id=service_id)
        item.delete()
        return Response({'detail':'removed'})

class OrderCreateFromCartAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        items = cart.items.select_related('service')
        if not items.exists():
            return Response({'detail':'cart empty'}, status=400)
        order = Order.objects.create(user=request.user, status='pending')
        total = 0
        for it in items:
            subtotal = it.quantity * it.service.price
            OrderItem.objects.create(
                order=order,
                service=it.service,
                service_title=it.service.title,
                unit_price=it.service.price,
                quantity=it.quantity,
                subtotal=subtotal
            )
            total += subtotal
        order.total_amount = total
        order.save()
        # clear cart
        items.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=201)

class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def perform_create(self, serializer):
        # optional: check that user had order with that service and status completed
        serializer.save(user=self.request.user)
