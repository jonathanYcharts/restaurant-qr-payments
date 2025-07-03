from django.contrib import admin
from django.urls import path

from orders.views import get_table_orders, create_checkout_session


urlpatterns = [
    path("admin/", admin.site.urls),
    # Restaurant-specific table access
    path("restaurant/<int:restaurant_id>/mesa/<int:table_number>/", get_table_orders),
    # Checkout session creation (also scoped to restaurant)
    path("restaurant/<int:restaurant_id>/create-checkout-session/", create_checkout_session),
]
