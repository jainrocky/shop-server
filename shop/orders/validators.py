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


def offer_applicability_validator(order, offer, bought_qty, amount_before_discount, *args, **kwargs):
    if offer.given_by == 'store':
        errors = {}
        min_qty, min_amount = offer.min_qty, offer.min_amount
        off_amount, off_percent = offer.off_amount, offer.off_percent
        off_upto = offer.off_upto
        if offer.level == 'productlevel':
            # Ensuring applicability.
            if min_qty and not min_qty <= bought_qty:
                errors['min_qty'] = [
                    'Must be greater then or equal to bought_qty'
                ]
            if min_amount and not min_amount <= amount_before_discount:
                errors['min_amount'] = [
                    'Must be greater then or equal to Net amount without discount.'
                ]
        elif offer.level == 'orderlevel':
            # Ensuring applicability.
            total_products = order.products.count()
            order_amount = order.amount
            # counting self also
            if min_qty and not min_qty <= (total_products + 1):
                errors['min_qty'] = [
                    'Must be greater then or equal to net order quantity.'
                ]
            if min_amount and not min_amount <= (order_amount + amount_before_discount):
                errors['min_amount'] = [
                    'Must be greater then or equal to net order amount without discount.'
                ]
        if errors:
            raise serializers.ValidationError({
                'errors': errors
            })
