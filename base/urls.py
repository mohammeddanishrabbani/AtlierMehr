from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf.urls.static import static 
from django.conf import settings 
from . import views
urlpatterns = [
    path('',views.home,name='home'),
    path('main/',views.main,name='main'),
    path('shop/',views.shop,name='shop'),
    path('detail/<int:id>/', views.detail_view, name='detail'),
    path('add-to-cart/<str:pk>/', views.add_to_cart, name='add-to-cart'),
    path('cart/',views.order_summary,name='cart'),
    path('remove-from-cart/<str:pk>',views.remove_from_cart,name='remove-from-cart'),
    path("remove_single_item_from_cart/<str:pk>",views.remove_single_item_from_cart, name="remove_single_item_from_cart"),
    path('checkout/',views.checkout,name='checkout')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)