from django.urls import path
from . import views
from . import views_manage

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart & AJAX endpoints
    path('cart/', views.cart_view, name='cart'),
    path('cart/add_ajax/<int:pk>/', views.add_to_cart_ajax, name='add_to_cart_ajax'),
    path('cart/update_ajax/', views.cart_update_ajax, name='cart_update_ajax'),
    path('cart/summary_ajax/', views.cart_summary_ajax, name='cart_summary_ajax'),
    path('cart/checkout_prepare/', views.checkout_prepare, name='checkout_prepare'),
    path('cart/update/<str:pid>/', views.cart_update, name='cart_update'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_confirmation, name='order_confirmation'),


]
