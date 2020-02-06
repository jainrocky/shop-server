from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,
)

import json
from json import JSONDecodeError


from .handlers import (
    get_serializer_and_model_or_404,
    process_fields_query,
    process_sort_query,
    process_ids_query,
)
from .models import (
    UserProfile,
    UserHistory,
    User,
)
from .serializers import (
    UserProfileSerializer,
    UserHistorySerializer,
    UserSerializer,
)

EXTRA_PARAMS = {
    'FIELDS': 'fields',
    'SORT': 'sort',
    'Q': 'q',
    'IDS': 'ids',
}


@api_view(['POST', ])
def login(request,):
    phone = request.POST.get('phone', None)
    password = request.POST.get('password', None)
    if phone and password:
        try:
            user = User.objects.get(phone=phone)
            if not user.check_password(password):
                return Response({
                    "errors": ['Invalid password.']
                }, status=status.HTTP_401_UNAUTHORIZED, )
            serializer = UserSerializer(user)
            return Response({
                "success": serializer.data
            }, status=status.HTTP_200_OK, )
        except:
            return Response({
                "errors": ['Invalid phone.']
            }, status=status.HTTP_400_BAD_REQUEST, )
    else:
        return Response({
            "errors": ['phone and password both are required.']
        }, status=status.HTTP_400_BAD_REQUEST, )


@api_view(['POST', ])
def register(request, ):
    serializer_class, model = UserSerializer, User
    serializer = serializer_class(
        data=request.data, context={'request': request})
    if serializer.is_valid(raise_exception=False):
        new_record = serializer.save()
        return Response({
            "success": serializer_class(new_record).data
        })
    return Response({
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST, )


# /users/all?fields=&sort=
# /histories/all?fields=&sort=

@api_view(['GET', ])
@permission_classes([IsAdminUser, ])
def all_users(request, *args, **kwargs):
    serializer_class, model = UserProfileSerializer, UserProfile
    paginator = PageNumberPagination()
    raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
    try:
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            'errors': {
                'fields': ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST,)
    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)

    query_set = model.objects.all().order_by(sort)
    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', ])
@permission_classes([IsAdminUser, ])
def all_histories(request, *args, **kwargs):
    serializer_class, model = UserHistorySerializer, UserHistory
    paginator = PageNumberPagination()
    raw_fields = request.GET.get(EXTRA_PARAMS['FIELDS'], None)
    try:
        fields = process_fields_query(raw_fields)
    except JSONDecodeError:
        return Response({
            'errors': {
                'fields': ['Value must be valid JSON.']
            }
        }, status=status.HTTP_400_BAD_REQUEST,)
    sort_query = request.GET.get(EXTRA_PARAMS['SORT'], None)
    sort = process_sort_query(sort_query, model)

    query_set = model.objects.all().order_by(sort)
    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# /users/list?ids=[]&sort=&fields=
@api_view(['GET', ])
@permission_classes([IsAdminUser, ])
def list_users(request, *args, **kwargs):
    serializer_class, model = UserProfileSerializer, UserProfile
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
    query_set = model.objects.filter(user__id__in=ids).order_by(sort)
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(query_set, request)
    serializer = serializer_class(
        page, many=True, fields=fields, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

# /users/update/profiles/
# Update profile for current requesting account only
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def update_profile(request, ):
    serializer_class = UserProfileSerializer
    serializer = serializer_class(
        request.user.profile, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        updated_record = serializer.save()
        return Response({
            "success": serializer_class(updated_record).data
        })
    return Response({
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST, )

    # /histories/search?user_id=&product_id=&user_name=&product_name=&ETC

    # discuss on that whether it should be automatic or mannually
    # /histories/update/<int:id>/
