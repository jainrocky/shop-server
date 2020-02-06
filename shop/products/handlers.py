import json
from django.http import Http404


from .serializers import (
    ProductSerializer,
    ProductCategorySerializer,
    ProductCategorySerializer,
    ProductImageSerializer,
    ManufacturerSerializer,
    OfferImageSerializer,
    OfferSerializer,
)

from .models import (
    Product,
    ProductCategory,
    ProductImage,
    Manufacturer,
    Offer,
    OfferImage
)


def get_serializer_and_model_or_404(object, ):
    if object == 'products':
        serializer_class, model = ProductSerializer, Product
    elif object == 'categories':
        serializer_class, model = ProductCategorySerializer, ProductCategory
    elif object == 'manufacturers':
        serializer_class, model = ManufacturerSerializer, Manufacturer
    elif object == 'offers':
        serializer_class, model = OfferSerializer, Offer
    else:
        raise Http404
    return serializer_class, model


def process_sort_query(query, model, ):
    sort = query
    if sort and (hasattr(model, sort) or (sort[0] is '-' and hasattr(model, sort[1:]))):
        return sort
    return '-created'


def process_fields_query(query, ):
    if query:
        return json.loads(query)
    return None


def process_ids_query(query, ):
    if query:
        return json.loads(query)
    return None


# validators
