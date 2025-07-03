import json
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import Restaurant, Order

stripe.api_key = settings.TEST_STRIPE_SECRET_KEY

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
