from django.contrib import admin
from django.urls import path

from orders.views import get_table_orders, create_checkout_session, RestaurantDashboardView, login_view, logout_view, activate_view, check_auth_view


urlpatterns = [
    path("admin/", admin.site.urls),
    # Restaurant-specific table access
    path("restaurant/<int:restaurant_id>/mesa/<int:table_number>/", get_table_orders),
    # Checkout session creation (also scoped to restaurant)
    path("restaurant/<int:restaurant_id>/create-checkout-session/", create_checkout_session),
    # Protected Restaurant dashboard view
    path("dashboard/", RestaurantDashboardView.as_view(), name='restaurant-dashboard'),
    path("api/login/", login_view),
    path("api/logout/", logout_view),
    path("api/check-auth/", check_auth_view),
    path("api/activate/", activate_view),
]
