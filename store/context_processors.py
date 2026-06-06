from store.models import CartItem 

def cart_item_count(request) : 
    if request.user.is_authenticated : 
        cart_items = CartItem.objects.filter(user = request.user)
        count = sum(item.quantity for item in cart_items)
    else : 
        count = 0 
    
    return {"cart_item_count" : count}