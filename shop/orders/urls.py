from django.urls import path
from orders.views import (
    orders,
    carts_to_orders,
    update_orders,
    all_orders,

    logged_user_all_carts,
    carts,
    add_cart,
    update_cart,
    delete_cart_items,

)

urlpatterns = [
    path('orders/<int:id>/', orders, name='orders'),
    path('orders/all/', all_orders, name='all_orders'),
    path('carts/to-orders/<int:cart_id>/',
         carts_to_orders, name='carts_to_orders'),
    path('orders/update/<int:id>/', update_orders, name='update_orders'),

    path('carts/<int:id>/', carts, name='carts'),
    path('carts/all/', logged_user_all_carts, name='logged_user_all_carts'),
    path('carts/add/', add_cart, name='add_carts', ),
    path("carts/update/<int:id>/", update_cart, name="update_carts"),

    # delete cart items
    path('carts/<int:cart_id>/items/<item_id>/',
         delete_cart_items, name='delete_cart_items'),
]
