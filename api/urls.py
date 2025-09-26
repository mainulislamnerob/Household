from django.urls import path, include
from rest_framework.routers import DefaultRouter
from service.views import ServiceViewSet, ReviewViewSet
import service.views as svc_views

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('',include(router.urls)),
    path('api/cart/', svc_views.CartView.as_view()),
    path('api/cart/add/', svc_views.AddToCartAPIView.as_view()),
    path('api/cart/remove/', svc_views.RemoveFromCartAPIView.as_view()),
    path('api/orders/create-from-cart/', svc_views.OrderCreateFromCartAPIView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]