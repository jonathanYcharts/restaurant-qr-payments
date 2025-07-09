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

from .models import Restaurant, Order, RegistrationToken, RestaurantUser, MenuItem, OrderItem


stripe.api_key = settings.TEST_STRIPE_SECRET_KEY


@method_decorator(login_required, name='dispatch')
class RestaurantDashboardView(View):
    def get(self, request):
        user = request.user
        restaurant = request.user.restaurant
        if not restaurant:
            return JsonResponse({'error': 'No restaurant assigned to this user.'}, status=403)

        orders = []
        for order in restaurant.orders.prefetch_related('items').order_by('-created_at'):
            orders.append({
                'id': order.id,
                'table_number': order.table_number,
                'status': order.status,
                'created_at': order.created_at,
                'updated_at': order.updated_at,
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'price': float(item.price_at_order),
                        'quantity': item.quantity,
                        'quantity_paid': item.quantity_paid,
                    }
                    for item in order.items.all()
                ]
            })

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
            'name': item.name,
            'price': float(item.price_at_order),
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


# DASHBOARD - MENU ITEMS ====================
@csrf_exempt
@login_required
def add_menu_item(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        name = data.get('name')
        price = data.get('price')
        available = data.get('available', True)

        if not name or not price:
            return JsonResponse({'error': 'Missing fields'}, status=400)

        restaurant = request.user.restaurant
        item = MenuItem.objects.create(
            restaurant=restaurant,
            name=name,
            price=price,
            available=available,
        )
        return JsonResponse({
            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'available': item.available
            }
        })
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def update_menu_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = get_object_or_404(MenuItem, id=item_id, restaurant=request.user.restaurant)

        item.name = data.get('name', item.name)
        item.price = data.get('price', item.price)
        item.available = data.get('available', item.available)
        item.save()

        return JsonResponse({
            'item': {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'available': item.available
            }
        })
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def delete_menu_item(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(MenuItem, id=item_id, restaurant=request.user.restaurant)
        item.delete()
        return JsonResponse({'deleted_id': item_id})
    return JsonResponse({'error': 'POST required'}, status=400)


# DASHBOARD - ORDERS ====================
@csrf_exempt
@login_required
def create_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_number = data.get('table_number')

        if not table_number:
            return JsonResponse({'error': 'Missing table number'}, status=400)

        restaurant = request.user.restaurant

        # Void multiple "Open" or "Partially paid orders" in the same table
        existing_order = Order.objects.filter(
            restaurant=restaurant,
            table_number=table_number,
            status__in=['open', 'partial']
        ).first()

        if existing_order:
            return JsonResponse({
                'error': 'Ya existe una orden activa (open o partial) para esta mesa.',
                'existing_order_id': existing_order.id,
                'status': existing_order.status,
            }, status=409)

        # Continue with order creation
        order = Order.objects.create(restaurant=restaurant, table_number=table_number)

        return JsonResponse({
            'id': order.id,
            'table_number': order.table_number,
            'status': order.status,
            'created_at': order.created_at,
        })
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return JsonResponse({'error': 'Invalid status'}, status=400)

        order = get_object_or_404(Order, id=order_id, restaurant=request.user.restaurant)


        # Void multiple "Open" or "Partially paid orders" in the same table
        if new_status in ['open', 'partial']:
            conflict = Order.objects.filter(
                restaurant=order.restaurant,
                table_number=order.table_number,
                status__in=['open', 'partial']
            ).exclude(id=order.id).first()

            if conflict:
                return JsonResponse({
                    'error': 'Ya existe otra orden activa (open o partial) para esta mesa.',
                    'conflicting_order_id': conflict.id,
                    'status': conflict.status,
                }, status=409)

        # Validación especial si se desea cambiar a 'partial'
        if new_status == 'partial':
            paid_items = data.get('paid_items', [])

            if not paid_items:
                return JsonResponse({'error': 'Debes indicar qué productos han sido pagados.'}, status=400)

            if not order.items.exists():
                return JsonResponse({'error': 'No puedes poner en partial una orden vacía.'}, status=400)

            item_map = {item.id: item for item in order.items.all()}

            for paid in paid_items:
                item_id = paid.get('item_id')
                quantity_paid = paid.get('quantity_paid')

                if item_id not in item_map:
                    return JsonResponse({'error': f'Item {item_id} no pertenece a esta orden.'}, status=400)

                item = item_map[item_id]

                if quantity_paid < 0 or quantity_paid > item.quantity:
                    return JsonResponse({'error': f'Cantidad pagada inválida para item {item_id}.'}, status=400)

                item.quantity_paid = quantity_paid
                item.save()

            # Verificamos si ya todos están pagados totalmente
            if all(item.is_fully_paid for item in order.items.all()):
                order.status = 'paid'
            else:
                order.status = 'partial'

            order.save()
            return JsonResponse({'success': True, 'new_status': order.status})

        order.status = new_status
        order.save()
        return JsonResponse({'success': True, 'new_status': order.status})
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def add_item_to_order(request, order_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        menu_item_id = data.get('menu_item_id')
        quantity = int(data.get('quantity', 1))

        if not menu_item_id:
            return JsonResponse({'error': 'Missing menu item'}, status=400)

        menu_item = get_object_or_404(MenuItem, id=menu_item_id, restaurant=request.user.restaurant)
        order = get_object_or_404(Order, id=order_id, restaurant=request.user.restaurant)

        if order.status in ['paid', 'canceled']:
            return JsonResponse({'error': 'No se puede agregar productos a una orden pagada o cancelada.'}, status=403)
            
        item = OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            name=menu_item.name,
            price_at_order=menu_item.price,
            quantity=quantity,
        )

        return JsonResponse({
            'item': {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'price': float(item.price_at_order),
            }
        })
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def update_order_item(request, item_id):
    if request.method == 'POST':
        data = json.loads(request.body)

        item = get_object_or_404(OrderItem, id=item_id, order__restaurant=request.user.restaurant)
        order = item.order

        if order.status in ['paid', 'canceled']:
            return JsonResponse({'error': 'No se puede modificar una orden pagada o cancelada.'}, status=403)
            

        quantity = data.get('quantity')
        price = data.get('price')

        item = get_object_or_404(OrderItem, id=item_id, order__restaurant=request.user.restaurant)

        if quantity is not None:
            item.update_quantity(int(quantity))
        if price is not None:
            item.price_at_order = float(price)

        item.save()

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
@login_required
def delete_order_item(request, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    item = get_object_or_404(OrderItem, id=item_id, order__restaurant=request.user.restaurant)
    order = item.order

    if order.status in ['paid', 'canceled']:
        return JsonResponse({'error': 'No se puede eliminar ítems de una orden pagada o cancelada.'}, status=403)

    item.delete()
    return JsonResponse({'deleted': item_id})
