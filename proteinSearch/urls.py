from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_products(request):
    return redirect('product_list')

urlpatterns = [
    path('', redirect_to_products),  # root redirects to /products/
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/review/', views.submit_review, name='submit_review'),
]