from django.contrib import admin
from .models import Product, ProductCategory, ProductImage, Manufacturer, Offer, OfferImage

admin.site.register(Manufacturer)

admin.site.register(Product)
admin.site.register(ProductCategory)
admin.site.register(ProductImage)

admin.site.register(Offer)
admin.site.register(OfferImage)
