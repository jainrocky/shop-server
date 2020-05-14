from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from json import JSONDecodeError
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)

from orders.serializers import(
    OrderSerializer,
    PaymentSerializer,
    FreezeProductSerializer,
    ItemSerializer,
    CartItemListSerializer,
    CartCreateOrUpdateSeriralizer,
    CartToOrderSerializer,
)

from orders.models import(
    Order,
    Payment,
    Cart,
    Item
)

from .handlers import (
    process_sort_query,
    process_fields_query,
    process_ids_query,
)


'''
    EXTRA PARAMS USED
'''
EXTRA_PARAMS = {
    'FIELDS': 'fields',
    'SORT': 'sort',
    'Q': 'q',
    'IDS': 'ids',
}

#  ---------------------------------------------
# |                ORDERS                       |
#  ---------------------------------------------

# NOTE: ADMIN CAN VIEW ANY ORDER EXCEPT ORDER HAVING SAVED STATUS
# /orders/all/
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def all_orders(request, *args, **kwargs):
    serializer_class, model = OrderSerializer, Order
    paginator = PageNumberPagination()
    try:
        # must be Json array having 'n' strings
        raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)

    query_set = None
    if request.user.is_staff:
        # NOTE: Hardcoded status not included saved orders
        query_set = model.objects.filter(~Q(status='saved')).order_by(sort)
    else:
        query_set = request.user.orders.all().order_by(sort)

    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# /orders/<int:id>/
@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def orders(request, id, *args, **kwargs):
    try:
        # must be Json array having 'n' strings
        raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    order = None
    try:
        if request.user.is_staff:
            order = Order.objects.get(Q(id=id), ~Q(status='saved'))
        else:
            order = request.user.orders.get(id=id)
    except ObjectDoesNotExist:
        return Response({
            'errors': {
                'order': ['Does not exist.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        OrderSerializer(order, fields=fields).data,
        status=status.HTTP_200_OK,
    )

# /carts/to-orders/<int:cart_id>/
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def carts_to_orders(request, cart_id, *args, **kwargs):
    try:
        cart = request.user.carts.get(id=cart_id)
    except ObjectDoesNotExist:
        return Response({
            'errors': {'cart': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST, )
    ser = CartToOrderSerializer(
        cart,
        data=request.data,
        context={
            'request': request,
        }
    )
    if ser.is_valid():
        cart = ser.save()
        return Response(
            OrderSerializer(cart.order).data,
            status=status.HTTP_200_OK,
        )
    return Response(
        ser.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

# /orders/update/<int:id>
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def update_orders(request, id, *args, **kwargs):
    try:
        order = request.user.orders.get(id=id)
    except ObjectDoesNotExist:
        return Response({
            'errors': {'order': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST)
    ser = OrderSerializer(
        order,
        data=request.data,
        context={
            'request': request,
        }
    )
    if ser.is_valid():
        updated_order = ser.save()
        return Response(ser.data, status=status.HTTP_200_OK)
    return Response({
        "errors": ser.errors
    }, status=status.HTTP_400_BAD_REQUEST, )

#  ---------------------------------------------
# |                CARTS                        |
#  ---------------------------------------------

# carts/<int:id>
@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def carts(request, id, *args, **kwargs):
    try:
        # must be Json array having 'n' strings
        raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart = request.user.carts.get(id=id)
    except ObjectDoesNotExist:
        return Response({
            'errors': {'cart': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        CartItemListSerializer(cart, fields=fields).data,
        status=status.HTTP_200_OK,
    )


# /carts/all/
@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def logged_user_all_carts(request, *args, **kwargs):
    try:
        # must be Json array having 'n' strings
        raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, Cart)
    carts = request.user.carts.all().order_by(sort)
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(carts, request)
    ser = CartItemListSerializer(
        page,
        many=True,
        fields=fields,
    )
    return paginator.get_paginated_response(ser.data)

# /carts/add/
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def add_cart(request, *args, **kwargs):
    ser = CartCreateOrUpdateSeriralizer(
        data=request.data,
        context={'request': request}
    )
    if ser.is_valid():
        cart = ser.save()
        return Response(
            CartItemListSerializer(cart).data,
            status=status.HTTP_201_CREATED,
        )
    return Response({
        "errors": ser.errors
    }, status=status.HTTP_400_BAD_REQUEST, )

# carts/update/<int:id>/
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def update_cart(request, id, *args, **kwargs):
    try:
        # serach only in user carts list
        cart = request.user.carts.get(id=id)
    except ObjectDoesNotExist:
        return Response({
            "errors": {'cart': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST, )
    ser = CartCreateOrUpdateSeriralizer(
        cart,
        data=request.data,
        context={
            'request': request,
        }
    )
    if ser.is_valid():
        updated_cart = ser.save()
        return Response(CartItemListSerializer(updated_cart).data, status=status.HTTP_200_OK,)
    return Response({
        "errors": ser.errors
    }, status=status.HTTP_400_BAD_REQUEST, )

# /carts/<int:cart_id>/items/<int:item_id>/
@api_view(['DELETE', ])
@permission_classes([IsAuthenticated, ])
def delete_cart_items(request, cart_id, item_id, *args, **kwargs):

    try:
        # serach only in user carts list
        cart = request.user.carts.get(id=cart_id)
    except ObjectDoesNotExist:
        return Response({
            "errors": {'cart': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST, )

    try:
        item = cart.items.get(id=item_id)
    except ObjectDoesNotExist:
        return Response({
            "errors": {'item': ['Does not exist.']}
        }, status=status.HTTP_400_BAD_REQUEST, )
    item.delete()
    # delete cart is no items is left
    if cart.items.count() > 0:
        return Response(CartItemListSerializer(cart).data, status=status.HTTP_200_OK, )
    cart.delete()
    return Response({
        'success': ['Cart is deleted successfully']
    }, status=status.HTTP_200_OK, )
