from rest_framework import serializers
from django.utils.translation import gettext as _


def positive_integers_list_validator(value, *args, **kwargs):
    '''
        Excluding zero also
    '''
    for v in value:
        if not isinstance(v, int) or (isinstance(v, int) and v < 1):
            raise serializers.ValidationError(
                'Value must be positive JSONIntegers'
            )


def atleast_one_field_validator(fields, validated_data, *args, **kwargs):
    if not set(fields).intersection(set(validated_data.keys())):
        raise serializers.ValidationError({
            "errors": {
                "required": ['Atleast one field']
            }
        })


def more_images_and_rank_validator(data, *args, **kwargs):
    more_images, more_images_rank = data.get(
        'add_images', None), data.get('add_images_rank', None)
    if more_images and more_images_rank:
        if not len(more_images_rank) is len(more_images):
            raise serializers.ValidationError(
                {'add_images_rank': _(
                    'Length must be equals to more_images')}
            )
    elif more_images or more_images_rank:
        if more_images:
            raise serializers.ValidationError(
                {'add_images_rank': _('This field is required.')}
            )
        else:
            raise serializers.ValidationError(
                {'add_images': _('This field is required.')}
            )
    return data
