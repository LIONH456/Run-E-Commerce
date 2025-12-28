from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" class="admin-thumb" style="width:80px;height:120px;object-fit:cover;" />', obj.image_url)
        return '(no image)'
    image_tag.short_description = 'Image'

    def image_preview(self, obj):
        if obj and getattr(obj, 'image_url', None):
            # include identifiable img id for JS live preview (match list thumbnail size)
            return format_html('<div style="margin-top:8px"><img id="product-image-preview-img" src="{}" style="width:100px;height:150px;object-fit:cover;border-radius:4px;" /></div>', obj.image_url)
        # provide an empty placeholder element for JS to fill
        return mark_safe('<div style="margin-top:8px" id="product-image-preview">(no image)</div>')
    image_preview.short_description = 'Preview'

    list_display = ('product_id', 'image_tag', 'name', 'price', 'stock', 'status')
    # product_id is primary key and not editable - show it as readonly instead of a form field
    readonly_fields = ('product_id', 'image_preview')
    fields = ('name','description','price','stock','image_url','image_preview','status')
    search_fields = ('name',)

    class Media:
        js = ('admin/js/image_preview.js',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'customer_email', 'total_amount', 'created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order_item_id', 'order', 'product', 'quantity', 'subtotal')
