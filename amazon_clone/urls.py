"""
URL configuration for amazon_clone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from amazon_clone import views 
from django.contrib.auth import views as auth_views
from django.conf import settings 
from django.conf.urls.static import static 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , views.homePage , name = "home"),
    path("category/<slug:category_slug>/" , views.category , name = "category"),
    path("product/<int:pk>/" , views.product_detail , name = "product_detail"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html' , next_page='/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),  # custom register view
    path("cart/" , views.view_cart , name = "view_cart"),
    path("cart/add/<int:product_id>" , views.add_to_cart , name = "add_to_cart"),
    path("cart/decrease/<int:item_id>" , views.decrease_in_cart , name = "decrease_in_cart"),
    path("cart/delete/<int:item_id>" , views.delete_from_cart , name = "delete_from_cart"),
    path('my-orders/', views.my_orders, name='my_orders'),
    path("checkout/" , views.checkout , name = "checkout"),
    path("order-details/<int:order_id>" , views.order_details , name = "order_details"),
    path("order-success/" , views.order_success ,  name ="order_success"),
    path("orders/<int:order_id>/cancel/" , views.cancel_order ,name = "cancel_order"),
    path("buy-now/<int:product_id>" , views.buy_now , name = "buy_now"),
    path("search/" , views.search , name = "search"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Serve media files in production (Render)
    from django.views.static import serve
    from django.urls import re_path

    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]