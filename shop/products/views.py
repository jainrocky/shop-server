from .handlers import (
    process_sort_query,
    process_fields_query,
    process_ids_query,
    get_serializer_and_model_or_404
)

from .models import (
    Product,
    ProductCategory,
    ProductImage,
    Manufacturer,
    Offer,
    OfferImage
)
from accounts.models import UserHistory

from .serializers import (
    ProductSerializer,
    ProductCategorySerializer,
    ProductCategorySerializer,
    ProductImageSerializer,
    ManufacturerSerializer,
    OfferImageSerializer,
    OfferSerializer,
)
from django.db.models.fields.related import (
    ForeignKey,
    ManyToManyField,
    OneToOneField,
)

from rest_framework.parsers import FileUploadParser
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)


from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.http import JsonResponse
from django.db.models import Q
import io
import json
from json import JSONDecodeError


from rest_framework.decorators import parser_classes
from .utils import MultipartJsonParser
from rest_framework.parsers import JSONParser
from django.urls import reverse


'''
    EXTRA PARAMS USED
'''
EXTRA_PARAMS = {
    'FIELDS': 'fields',
    'SORT': 'sort',
    'Q': 'q',
    'IDS': 'ids',
}

# products/objects/all/


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
@permission_classes([IsAuthenticated])
def all_objects(request, object):
    serializer_class, model = get_serializer_and_model_or_404(object)
    paginator = PageNumberPagination()

    # must be Json array having 'n' strings
    raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
    try:
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)

    query_set = model.objects.all().order_by(sort)

    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# products/objects/<int: id>/
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def objects(request, object, id):
    serializer_class, model = get_serializer_and_model_or_404(object)
    try:
        raw_fields = request.query_params.get(EXTRA_PARAMS['FIELDS'])
        fields = process_fields_query(raw_fields)
    except:
        return Response({
            "errors": {
                "fields": ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    try:
        query_set = model.objects.get(id=id)
        # save to history.
        if object == 'products':
            history = UserHistory(
                user=request.user,
                product=query_set,
                source=request.GET.get('source', None),
                lat=request.GET.get('lat', None),
                lon=request.GET.get('lon', None),
            )
            history.save()
    except ObjectDoesNotExist:
        return Response({
            "errors": {
                object: ["Does not exist."]
            }
        }, status=status.HTTP_404_NOT_FOUND)
    serializer = serializer_class(query_set, fields=fields, context={
        'product_viewed': True,
    })
    return Response(serializer.data)

# products/objects/search/
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def search_objects(request, object):
    serializer_class, model = get_serializer_and_model_or_404(object)
    paginator = PageNumberPagination()
    kwargs = dict(request.GET.items())
    sort_query = kwargs.pop(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)
    errors = {}
    try:
        fields_query = kwargs.pop(EXTRA_PARAMS['FIELDS'], None)
        fields = process_fields_query(fields_query)
    except:
        errors[EXTRA_PARAMS['FIELDS']] = ['Value must be valid JSON.']

    exist = set([_.name for _ in model._meta.fields if not isinstance(_, (
        # ForeignKey,
        ManyToManyField,
        OneToOneField,
    ))])

    # fields to be exclude
    exclude = set(['active', 'created', 'id',
                   'limits', 'nos', 'qty', 'qty_unit',
                   'image', 'primary_image', 'raw_sub_categories',
                   'modified', 'total_left', 'total_sold', 'best_before',
                   ])
    # lookups for related fields
    related_fields_lookup = {
        'products': {
            'category': 'category__name__icontains',
            'manufacturer': 'manufacturer__name__icontains',
        }
    }
    # available fields for search operation
    avail = exist - exclude
    Q_set = None
    if EXTRA_PARAMS['Q'] in kwargs and kwargs[EXTRA_PARAMS['Q']]:
        for field in avail:
            lookup = None
            if field in related_fields_lookup[object]:
                lookup = related_fields_lookup[object][field]
            else:
                lookup = "%s__icontains" % field
            if Q_set:
                Q_set |= Q(**{lookup: kwargs[EXTRA_PARAMS['Q']]})
            else:
                Q_set = Q(**{lookup: kwargs[EXTRA_PARAMS['Q']]})
    # else:
    if True:
        valid_fields = avail.intersection(kwargs.keys())
        for field in valid_fields:
            lookup = None
            if field in related_fields_lookup[object]:
                lookup = related_fields_lookup[object][field]
            else:
                lookup = "%s__icontains" % field
            if not kwargs[field]:
                continue
            if Q_set:
                Q_set |= Q(**{lookup: kwargs[field]})
            else:
                Q_set = Q(**{lookup: kwargs[field]})
    if not Q_set:
        errors['required'] = [
            "Atleast one of them",
            "q, "+", ".join(avail)
        ]
    if errors:
        return Response({
            "errors": errors
        }, status=status.HTTP_400_BAD_REQUEST)
    query_set = model.objects.filter(Q_set).order_by(sort)
    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page,
        many=True,
        fields=fields,
        context={'request': request}
    )
    return paginator.get_paginated_response(serializer.data)


# products/objects/list/   query: Array of productId's
@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def list_objects(request, object):
    serializer_class, model = get_serializer_and_model_or_404(object)
    errors = {}
    try:
        raw_ids = request.query_params.get(EXTRA_PARAMS['IDS'])
        ids = process_ids_query(raw_ids)
        if not ids:  # ids must required
            errors['ids'] = ['This field is required.']
    except:
        errors['ids'] = ['Value must be valid JSON.']
    try:
        raw_fields = request.query_params.get(EXTRA_PARAMS['FIELDS'])
        fields = process_fields_query(raw_fields)
    except:
        errors['fields'] = ['Value must be valid JSON.']
    if errors:
        return Response({
            "errors": errors
        }, status=status.HTTP_400_BAD_REQUEST)
    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)

    query_set = model.objects.filter(id__in=ids).order_by(sort)
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


# products/objects/add/

@api_view(['POST'])
@permission_classes([IsAdminUser, ])
def add_objects(request, object):
    serializer_class, model = get_serializer_and_model_or_404(object)
    serializer = serializer_class(
        data=request.data, context={'request': request})
    if serializer.is_valid(raise_exception=False):
        new_record = serializer.save()
        return Response({
            "success": {
                object: serializer_class(new_record).data
            }
        }, status=status.HTTP_201_CREATED)
    return Response({
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST, )


# products/objects/update/<int: id>
@api_view(['POST'])
@permission_classes([IsAdminUser, ])
def update_objects(request, object, id):
    serializer_class, model = get_serializer_and_model_or_404(object)
    try:
        query_set = model.objects.get(id=id)
    except:
        return Response({
            "errors": {
                object: ['Does not exist.']
            }
        }, status=status.HTTP_400_BAD_REQUEST,)
    serializer = serializer_class(
        query_set, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        updated_record = serializer.save()
        return Response({
            "success": {
                object: serializer_class(updated_record).data
            }
        })
    return Response({
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST, )


# @api_view(['GET'])
# def most_viewed_products(request, ):
#     pass


'''
    To be impelmented
'''
# products/objects/batch-add/
@api_view(['POST'])
@parser_classes((MultipartJsonParser, JSONParser, ))
def batch_add_objects(request, object):
    # print(request.body)
    # print(json.loads(request.body))
    return JsonResponse({"msg": request.data})


# products/objects/batch-update/
@api_view(['POST'])
def batch_update_objects(request):
    # return Response({"msg": "HelloWorld"})
    return JsonResponse({"msg": "HelloWorld"})
