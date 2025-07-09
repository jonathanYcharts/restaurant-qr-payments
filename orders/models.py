import uuid
from django.db import models
from django.db.models import Q, UniqueConstraint

from django.contrib.auth.models import AbstractUser
from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RestaurantUser(AbstractUser):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True, blank=True)


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('paid', 'Fully Paid'),
        ('partial', 'Partially Paid'),
        ('canceled', 'Canceled'),
    ]

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    table_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Mesa {self.table_number} — {self.status}"
    
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['restaurant', 'table_number'],
                condition=Q(status__in=['open', 'partial']),
                name='unique_active_order_per_table_per_restaurant'
            )
        ]

    def clean(self):
        if self.status in ['open', 'partial']:
            existing = Order.objects.filter(
                table_number=self.table_number,
                status__in=['open', 'partial']
            ).exclude(pk=self.pk).exists()
            if existing:
                raise ValidationError(f"Table {self.table_number} already has an open/partially paid order.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    def calculate_status(self):
        items = self.items.all()
        if all(item.is_paid for item in items):
            return 'paid'
        elif any(item.is_paid for item in items):
            return 'partial'
        return 'open'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    quantity_paid = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} x{self.quantity} @ ${self.price_at_order}"

    def total_price(self):
        return self.price_at_order * self.quantity

    @property
    def is_fully_paid(self):
        return self.quantity_paid >= self.quantity

    @property
    def unpaid_quantity(self):
        return max(self.quantity - self.quantity_paid, 0)

    def update_quantity(self, new_quantity: int):
        if new_quantity < self.quantity_paid:
            raise ValueError("New quantity cannot be less than already paid quantity.")

        self.quantity = new_quantity
        self.save()


class RegistrationToken(models.Model):
    token = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)
