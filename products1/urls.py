from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
# Media Assets

from .views import (
    ProductDetailView,
    ProductListView,
    CreateStripeCheckoutSessionView,
    SuccessView,
    CancelView,
    StripeWebhookView,
)
app_name = "products1"
urlpatterns = [

    path("", ProductListView.as_view(), name="product-list"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product-detail"),

    path(
        "create-checkout-session/<int:pk>/",
        CreateStripeCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),

    path("success/", SuccessView.as_view(), name="success"),
    path("cancel/", CancelView.as_view(), name="cancel"),

    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)