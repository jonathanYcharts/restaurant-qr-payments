from django.db import models

class OrderItem(models.Model):
    table_number = models.IntegerField()
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)
