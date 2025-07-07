import json
import stripe

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout

from .models import Restaurant, Order, RegistrationToken, RestaurantUser


stripe.api_key = settings.TEST_STRIPE_SECRET_KEY


@method_decorator(login_required, name='dispatch')
class RestaurantDashboardView(View):
    def get(self, request):
        user = request.user
        restaurant = request.user.restaurant
        if not restaurant:
            return JsonResponse({'error': 'No restaurant assigned to this user.'}, status=403)

        orders = restaurant.orders.order_by('-created_at').values(
            'id', 'table_number', 'status', 'created_at', 'updated_at'
        )
        menu = restaurant.menu_items.values('id', 'name', 'price', 'available')

        return JsonResponse({
            'username': user.username,
            'email': user.email,
            'restaurant': restaurant.name,
            'orders': list(orders),
            'menu': list(menu),
        })


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data['username'], password=data['password'])
        if user:
            login(request, user)
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@login_required
def check_auth_view(request):
    user = request.user
    return JsonResponse({
        'username': user.username,
        'email': user.email,
        'restaurant': user.restaurant.name if user.restaurant else None,
    })


@csrf_exempt
def create_checkout_session(request, restaurant_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        # To do: Validate restaurant exists
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        line_items = []
        metadata = {}
        for item in data.get('items', []):
            item_id = str(item['id'])
            quantity = int(item['quantity'])

            # Build Stripe line item
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(float(item['price']) * 100),  # Stripe uses cents
                },
                'quantity': quantity,
            })
            metadata[item_id] = str(quantity)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            locale='auto',
            automatic_tax={'enabled': False},
            success_url='http://localhost:4200/success',
            cancel_url='http://localhost:4200/cancel',
            metadata=metadata,
            # Pending to decipher the tips shit
            # tip_settings={
            #     'enabled': True,
            #     'suggested_tip_percentages': [10, 15, 20],
            # },
        )

        return JsonResponse({'id': session.id})

    return JsonResponse({'error': 'POST request required'}, status=400)


def get_table_orders(request, restaurant_id, table_number):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    order = get_object_or_404(
        Order.objects.prefetch_related('items__menu_item'),
        restaurant=restaurant,
        table_number=table_number,
        status__in=['open', 'partial'] # only active orders
    )

    items = [
        {
            'id': item.id,
            'name': item.menu_item.name,
            'price': float(item.menu_item.price),
            'quantity': item.quantity,
            'quantity_paid': item.quantity_paid,
            'unpaid_quantity': item.unpaid_quantity,
            'is_paid': item.is_fully_paid,
        }
        for item in order.items.all()
    ]

    return JsonResponse({
        'id': order.id,
        'restaurant': {
            'id': restaurant.id,
            'name': restaurant.name,
        },
        'table': table_number,
        'status': order.status,
        'items': items,
    })


@csrf_exempt
def activate_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        username = data.get('username')
        password = data.get('password')
        restaurant_name = data.get('restaurant_name')

        if not all([token, username, password, restaurant_name]):
            return JsonResponse({'error': 'Missing fields'}, status=400)

        try:
            reg_token = RegistrationToken.objects.get(token=token, is_used=False)
        except RegistrationToken.DoesNotExist:
            return JsonResponse({'error': 'Invalid or used token'}, status=403)

        if RestaurantUser.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username taken'}, status=409)

        restaurant = Restaurant.objects.create(name=restaurant_name)
        user = RestaurantUser.objects.create_user(username=username, password=password, restaurant=restaurant)

        reg_token.is_used = True
        reg_token.save()

        login(request, user)
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Only POST method allowed'}, status=405)
