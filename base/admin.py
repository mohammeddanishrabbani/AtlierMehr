from django.contrib import admin

# Register your models here.
from .models import Address, Product,ProductImage,Topic,Order,OrderItem
 
class ProductImageAdmin(admin.StackedInline):
    model = ProductImage
 
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageAdmin]
 
    class Meta:
       model = Product
 
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Topic)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)