import json
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import OrderItem

stripe.api_key = settings.TEST_STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        line_items = []
        for item in data.get('items', []):
            line_items.append({
                'price_data': {
                    'currency': 'mxn',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(float(item['price']) * 100),  # Stripe uses cents
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='http://localhost:4200/success',
            cancel_url='http://localhost:4200/cancel',
        )

        return JsonResponse({'id': session.id})

    return JsonResponse({'error': 'POST request required'}, status=400)


def get_table_items(request, table_number):
    items = OrderItem.objects.filter(table_number=table_number, is_paid=False)
    data = [
        {'id': item.id, 'name': item.name, 'price': float(item.price)}
        for item in items
    ]
    return JsonResponse({'table': table_number, 'items': data})
