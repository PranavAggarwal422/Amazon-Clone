from django.db import models
from autoslug import AutoSlugField 
from django.contrib.auth.models import User 

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category_slug = AutoSlugField(populate_from = "name" , unique = True , null = True , default = None)
    def __str__(self):
        return self.name

class Product(models.Model):
    image_url = models.URLField(blank=True)
    name = models.CharField(max_length=500, unique = True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.FloatField(blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=100 , blank = True )
    
    specifications = models.JSONField(default = dict , blank=True)
    description = models.TextField(blank = True)
    features = models.JSONField(default = list , blank=True)

    rating = models.FloatField(default=0)
    num_reviews = models.IntegerField(default=0)
    popularity_score = models.IntegerField(default=0)

    in_stock = models.BooleanField(default=True)
    seller = models.CharField(max_length=200, blank = True)
    # def __str__(self):
    #     return self.name


class FilterOption(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100) 

    def __str__(self):
        return f"{self.category.name} - {self.field_name}"

class FilterOptionValue(models.Model):
    filter_option = models.ForeignKey(FilterOption, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)          # e.g., LG, Samsung, 1.5 Ton
    # def __str__(self):
    #     return f"{self.filter_option.field_name} - {self.value}"


class CartItem(models.Model) : 
    user = models.ForeignKey(User , on_delete = models.CASCADE)
    product = models.ForeignKey(Product , on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    
    def subtotal(self) : 
        return self.product.price*self.quantity 
    

class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    created_at = models.DateTimeField(auto_now_add=True)
    order_processed_at = models.DateTimeField(null=True, blank=True)
    order_shipped_at = models.DateTimeField(null=True, blank=True)
    order_delivered_at = models.DateTimeField(null=True, blank=True)
    order_cancelled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE , related_name = "order_items" )
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Preserved snapshot fields
    product_name = models.CharField(max_length=200)
    product_price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.URLField(blank=True, null = True)

    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)  # = quantity * product_price_at_order

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"