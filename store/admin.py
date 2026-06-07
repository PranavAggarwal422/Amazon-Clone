from django.contrib import admin
from .models import Product, Category, CartItem, Order, OrderItem

# Register your models here.

def generate_description(product):
    desc = f"{product.brand} {product.name} {product.category.name}\n\n"

    for key, value in product.specifications.items():
        desc += f"{key}: {value}\n"

    if product.features:
        desc += "\nFeatures:\n"
        for f in product.features:
            desc += f"- {f}\n"

    return desc.strip()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'in_stock')
    search_fields = ('name', 'brand')
    list_filter = ('category', 'brand', 'in_stock')

    def save_model(self, request, obj, form, change):
        if not obj.description:
            obj.description = generate_description(obj)
        super().save_model(request, obj, form, change)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin) : 
    list_display = ("user" , "product" , "quantity")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_price_at_order', 'quantity', 'subtotal', 'product_image']
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id' , 'user', 'total_price', 'payment_method', 'order_status', 'created_at','name', 'phone', 'address' ]
    list_filter = ['order_status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'name', 'phone', 'address']
    readonly_fields = ['created_at','total_price','payment_method','name','user','phone','address']
    inlines = [OrderItemInline]
