from django.db import models
from django.db.models import Q, F, When, DecimalField, Case, Value
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    discount = models.PositiveIntegerField(default=0)  # discount in percentage

    objects = models.Manager()  # Use custom manager

    def __str__(self):
        return self.name

    def apply_discount(self, discount_percentage):
        if discount_percentage > 0:
            self.objects.filter(id=self.id).update(
                price=F('price') * (Decimal(discount_percentage) / Decimal(100))
            )
    def update_quantity(self, quantity):
        if self.stock >= quantity:
            self.objects.filter(id=self.id).update(price=F('price') - quantity)

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    # TODO: change the customer_name with the User model
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"order {self.id} - {self.customer_name} - {self.status}"


# for search better
class ProductManager(models.Manager):
    def search_products(self, query):
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(price__icontains=query)
        )

    def available_or_discounted(self):
        return self.filter(Q(is_available=True) | Q(discount__gt=0))
