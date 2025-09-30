# api/urls.py  (app-level)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from service.views import (
    ServiceViewSet, ReviewViewSet, CartItemViewSet,
    CartMeView, CartDetailView,OrderViewSet
)
from users.views import TeamViewSet, ContactMessageViewSet
from shop.views import ProductViewSet

router = DefaultRouter()
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"orders", OrderViewSet, basename="order")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"contact-messages", ContactMessageViewSet, basename="contactmessage")
router.register(r"products", ProductViewSet, basename="product")

# Cart items CRUD via ViewSet
router.register(r"cart/items", CartItemViewSet, basename="cart-item")

urlpatterns = [
    # Router endpoints (list/retrieve/create/update/delete)
    path("", include(router.urls)),

    # Cart “me” (get current user’s cart summary)
    path("cart/", CartMeView.as_view(), name="cart-me"),

    # Optional cart detail by id — use the correct converter for your model
    # If Cart.pk is an AutoField/BigAutoField, use <int:pk>; only use <uuid:pk> if pk is a UUIDField.
    path("cart/<int:pk>/", CartDetailView.as_view(), name="cart-detail"),

    # Auth (Djoser)
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
]
