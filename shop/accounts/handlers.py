from .models import (
    User,
    UserHistory,
    UserProfile,
)

from .serializers import (
    UserHistorySerializer,
    UserProfileSerializer,
    UserSerializer,
)
from django.http import Http404
import json


def get_serializer_and_model_or_404(object, ):
    if object == 'users':
        serializer_class, model = UserProfileSerializer, UserProfile
    elif object == 'histories':
        serializer_class, model = UserHistorySerializer, UserHistory
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
