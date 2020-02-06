from django.contrib import admin
from .models import(
    Order,
    Payment,
    FreezeProduct,
    Cart,
    Item,

)
# Register your models here.

admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Cart)
admin.site.register(Item)
admin.site.register(FreezeProduct)
