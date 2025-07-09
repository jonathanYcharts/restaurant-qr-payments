from django.contrib import admin
from django.urls import path

from orders.views import (
    get_table_orders,
    create_checkout_session,
    RestaurantDashboardView,
    login_view,
    logout_view,
    activate_view,
    check_auth_view,
    add_menu_item,
    update_menu_item,
    delete_menu_item,

    create_order,
    update_order_status,
    add_item_to_order,
    update_order_item,
    delete_order_item,
)

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
    # Dashboard menu items
    path("menu/add/", add_menu_item),
    path("menu/update/<int:item_id>", update_menu_item),
    path("menu/delete/<int:item_id>", delete_menu_item),
    # Dashboard orders
    path("order/create/", create_order),
    path("order/update-status/<int:order_id>", update_order_status),
    path("order/add-item/<int:order_id>", add_item_to_order),
    path("order/update-item/<int:item_id>", update_order_item),
    path("order/delete/<int:item_id>", delete_order_item),
]
