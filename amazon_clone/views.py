from django.shortcuts import render, redirect , get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.utils import timezone
from django.db.models import Q

from store.models import Category, Product, CartItem , Order , OrderItem
from store.semantic_search import semantic_search
from store.rerank import rerank_products
from store.ranking import calculate_score
from store.filter_builder import build_filters
from store.recommendations import get_similar_products, get_personalized_recommendations
from store.keyword_search import keyword_search

def register(request) : 
    if request.method == "POST" : 
        form = CustomUserCreationForm(request.POST)
        if form.is_valid() : 
            form.save() 
            return redirect("login")
    else : 
        form = CustomUserCreationForm() 
    return render(request , "register.html" , {"form" : form})

def homePage(request) :
    recommendations = []
    if request.user.is_authenticated:
        recommendations = get_personalized_recommendations(request.user)
 
    return render(request, "index.html", {"recommendations": recommendations})

def category(request, category_slug):
    category_obj = get_object_or_404(Category, category_slug=category_slug)
    products = Product.objects.filter(category=category_obj)
    data = {
        "products": products,
        "filter_options": build_filters(products)
    }
    return render(request, "category.html", data)

def product_detail(request, pk):
    product = Product.objects.get(id = pk)
    similar_products = get_similar_products(product)

    return render(request, "product.html",
        {
            "product": product,
            "similar_products": similar_products,
        }
    )

@login_required
def view_cart(request) : 
    cart_items = CartItem.objects.filter(user = request.user)
    total_price = sum(item.subtotal() for item in cart_items)
    return render(request, "cart.html" , {"cart_items" : cart_items   , "total_price" : total_price})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")

@login_required
def decrease_in_cart(request , item_id) : 
    if request.method == "POST" : 
        cart_item = get_object_or_404(CartItem , id = item_id , user = request.user) # ensure the logged-in user owns it
        if(cart_item.quantity == 1) : 
            cart_item.delete()
        else : 
            cart_item.quantity -= 1 
            cart_item.save()
    
    return redirect("view_cart")

@login_required
def delete_from_cart(request , item_id) : 
    if request.method == "POST" :
        cart_item = get_object_or_404(CartItem , id = item_id , user = request.user)
        cart_item.delete() 
    return redirect("view_cart")


@login_required
def checkout(request) : 
    cart_items = CartItem.objects.filter(user = request.user)
    total_price = sum(item.subtotal() for item in cart_items)

    if request.method == "POST" : 
        address = request.POST.get("address") 
        phone = request.POST.get("phone")
        name = request.POST.get("name")
        payment_method = request.POST.get("payment_method")
        # Create the order
        order = Order(address = address , phone = phone , name = name , payment_method = payment_method , user = request.user , total_price = total_price)
        order.save()

        # Create order items
        for item in cart_items : 
            OrderItem.objects.create(order = order , product = item.product , quantity = item.quantity , subtotal = item.subtotal() , product_name = item.product.name , product_price_at_order = item.product.price , product_image = item.product.image_url)

        # Clear cart
        cart_items.delete()
        request.session['order_id'] = order.id
        return redirect("order_success")
    return render(request , "checkout.html" , {"cart_items" : cart_items , "total_price" : total_price})


def order_success(request):
    order_id = request.session.pop('order_id', None)

    if not order_id:
        return redirect('home')
    
    return render(request, 'order_success.html', {'order_id': order_id})

@login_required
def my_orders(request) : 
    orders = Order.objects.filter(user = request.user).order_by("-id") ; 
    return render(request , "my_orders.html" ,  {"orders" : orders})

@login_required
def order_details(request , order_id) : 
    order = get_object_or_404(Order , id = order_id , user = request.user)
    return render(request , "order_details.html" , {"order" : order})

@login_required
def cancel_order(request , order_id) : 
    order = get_object_or_404(Order , id = order_id , user = request.user)
    if order.order_status in ['placed', 'processing']:
        order.order_status = "cancelled" 
        order.order_cancelled_at = timezone.now()
        order.save()
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.error(request, "Order cannot be cancelled at this stage.")

    return redirect('order_details', order_id=order_id)   


@login_required 
def buy_now(request , product_id) : 
    product = get_object_or_404(Product, id= product_id)
    if request.method == "POST" : 
        address = request.POST.get("address") 
        phone = request.POST.get("phone")
        name = request.POST.get("name")
        payment_method = request.POST.get("payment_method")

        # Create the order
        order = Order(address = address , phone = phone , name = name , payment_method = payment_method , user = request.user , total_price = product.price)
        order.save()

        # Create order items
       
        OrderItem.objects.create(order = order , product = product , quantity = 1 , subtotal = product.price , product_name = product.name , product_price_at_order = product.price , product_image = product.image_url)

        request.session['order_id'] = order.id
        return redirect("order_success")

    return render(request , "checkout.html" , {"product" : product , "total_price" : product.price})
    

def search(request):
    query = request.GET.get("q", "").strip()
    selected_brands = request.GET.getlist("brand")
    selected_categories = [c for c in request.GET.getlist("category") if c]

    if not query:
        return redirect("home")

    # Semantic search
    search_results = semantic_search(query)
    product_ids = [product_id for product_id, score in search_results]
    products_dict = Product.objects.in_bulk(product_ids)

    semantic_products = [
        products_dict[pid]
        for pid in product_ids
        if pid in products_dict
    ]

    # Keyword search
    keyword_products = keyword_search(query)

    # Merge both results without duplicates
    products = []
    seen_ids = set()

    for product in semantic_products + keyword_products:
        if product.id not in seen_ids:
            products.append(product)
            seen_ids.add(product.id)

    # Build filters BEFORE applying filters
    all_filter_options = build_filters(products)

    # Apply selected brand filters
    if selected_brands:
        selected_brands = {brand.lower() for brand in selected_brands}
        products = [
            p for p in products
            if p.brand.lower() in selected_brands
        ]

    # Apply selected category filters
    if selected_categories:
        selected_categories = {c.lower() for c in selected_categories}
        products = [
            p for p in products
            if p.category.name.lower() in selected_categories
        ]

    # Cohere rerank
    products = rerank_products(query, products)

    # Ranking based on rating, reviews and popularity_score
    products = sorted(products, key = calculate_score, reverse=True)

    # Show only top 10
    products = products[:10]

    # Store all selected filters generically
    selected_filters = {}

    for key in request.GET:
        selected_filters[key] = request.GET.getlist(key)

    data = {
        "products": products,
        "filter_options": all_filter_options,
        "selected_filters": selected_filters,
    }

    return render(request, "category.html", data)

