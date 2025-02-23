from django.db import models
from django.db.models import Q, F
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
    discount = models.PositiveIntegerField(default=0)

    objects = models.Manager()  # Use custom manager

    def __str__(self):
        return self.name

    def final_price(self):
        if self.discount != 0:
            return self.price - (self.price * Decimal(self.discount) / 100)
        return self.price

    #TODO: study this func
    def decrease_stock(self, quantity):
        if self.stock >= quantity:
            Product.objects.filter(id=self.id, stock__gte=quantity).update(stock=F('stock') - quantity)


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


class User(models.Model):
    pass


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
