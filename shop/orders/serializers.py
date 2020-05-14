from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

from orders.validators import (
    positive_integers_list_validator,
    atleast_one_field_validator,
    offer_applicability_validator,
)

from orders.models import (
    Order,
    Payment,
    FreezeProduct,
    Cart,
    Item,
)

from products.models import(
    Offer,
    Product,
)

from accounts.serializers import (
    UserSerializer,
    UserProfileSerializer
)
from products.serializers import(
    OfferSerializer,
    ProductSerializer,
)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            if existing.intersection(allowed):
                for field_name in existing - allowed:
                    self.fields.pop(field_name)


class PaymentSerializer(DynamicFieldsModelSerializer):
    pass


class FreezeProductSerializer(DynamicFieldsModelSerializer):
    original = ProductSerializer(
        read_only=True, fields=('id', 'name', 'primary_image',))
    applied_offer = OfferSerializer(
        read_only=True, fields=('id', 'name')
    )

    class Meta:
        model = FreezeProduct
        fields = '__all__'


class OrderSerializer(DynamicFieldsModelSerializer):
    products = FreezeProductSerializer(read_only=True, many=True, )
    user = serializers.SerializerMethodField()

    def get_user(self, instance, *args, **kwargs):
        return UserProfileSerializer(instance.user.profile, fields=('id', 'full_name', 'avatar',)).data

    class Meta:
        model = Order
        fields = '__all__'
        # exclude = ['user']
        extra_kwargs = {
            "amt_by_price": {'read_only': True},
            "amt_by_mrp": {'read_only': True},
            "discount_sum": {'read_only': True},
            "charges": {'read_only': True},
            "amount": {'read_only': True},
            'active': {'default': True, },
        }

    def update(self, instance, validated_data, *args, **kwargs):
        instance.favourite = validated_data.get(
            'favourite', instance.favourite)
        instance.delivered_date = validated_data.get(
            'delivered_date', instance.delivered_date)
        instance.delivered_by = validated_data.get(
            'delivered_by', instance.delivered_by)
        instance.order_location = validated_data.get(
            'order_location', instance.order_location)
        instance.delivery_location = validated_data.get(
            'delivery_location', instance.delivery_location)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.active = validated_data.get('active', instance.active)
        instance.cancel_reason = validated_data.get(
            'cancel_reason', instance.cancel_reason)
        instance.status = validated_data.get('status', instance.status)
        if hasattr(instance, 'order') and not instance.status == 'saved':
            Cart.objects.filter(id=instance.cart.id).update(order=None)
        instance.save()
        return instance


class CartToOrderSerializer(DynamicFieldsModelSerializer):
    charges = serializers.DecimalField(
        default=0.0,
        write_only=True,
        max_digits=9,
        decimal_places=4,
    )

    class Meta:
        model = Cart
        fields = ['charges']

    def update(self, instance, validated_data, *args, **kwargs):
        # BUG: overriding old orders from same cart
        if instance.order:
            # if in any there is any previous unsuccessful cart to order request.
            # delete previous order if associate with this cart
            instance.order.products.all().delete()
            instance.order.delete()

        fp_products = []
        order_data = {
            'user': self.context['request'].user,
            'charges': validated_data.get('charges', (0.0)),
            'status': 'saved'
        }
        order_data['amt_by_mrp'] = sum(
            [item.product.mrp * (item.bought_qty / item.product.nos)
             for item in instance.items.all()]
        )
        order_data['amt_by_price'] = sum(
            [item.product.price * (item.bought_qty / item.product.nos)
             for item in instance.items.all()]
        )
        for item in instance.items.all():
            data = dict()
            product, offer, bought_qty = item.product, item.offer, item.bought_qty
            data['original'] = product
            data['freeze_mrp'] = product.mrp
            data['freeze_price'] = product.price
            data['freeze_nos'] = product.nos
            data['freeze_qty'] = product.qty
            data['freeze_qty_unit'] = product.qty_unit
            data['bought_qty'] = bought_qty
            if offer:
                data['applied_offer'] = offer
                if (offer.min_amount is not None and offer.min_amount <= order_data['amt_by_price']) or (offer.min_qty is not None and offer.min_qty <= bought_qty <= offer.max_qty):
                    if offer.off_amount:
                        data['discount'] = min(
                            offer.off_amount, offer.off_upto
                        )
                    elif offer.off_percent:
                        data['discount'] = min(
                            product.price *
                            (bought_qty / product.nos), offer.off_upto
                        )
            else:
                data['discount'] = Decimal(0.0)
            data['total_amount'] = round((
                product.price * (bought_qty / product.nos)) - data['discount'], 4)
            # add product to order as a freeze product.
            try:
                fp = FreezeProduct.objects.create(**data)
            except:
                # delete all before raising error
                for p in fp_products:
                    p.delete()
                raise serializers.ValidationError({
                    'errors': ['Unsuccessful: not able to add cart product #id:{}'.format(product.id)]
                })
            fp_products.append(fp)
        order_data['discount_sum'] = sum(
            [fp.discount for fp in fp_products]
        )
        order_data['amount'] = Decimal(order_data['amt_by_price']) + \
            Decimal(order_data['charges']) - \
            Decimal(order_data['discount_sum'])
        order = Order.objects.create(**order_data)
        order.products.add(*fp_products)
        order.save()
        instance.order = order
        instance.save()
        return instance


class ItemSerializer(DynamicFieldsModelSerializer):
    product = ProductSerializer(
        fields=('id', 'name', 'primary_image', 'mrp', 'price', 'nos', 'qty', 'qty_unit',), )
    offer = OfferSerializer(fields=('id', 'name', 'min_qty',
                                    'min_amount', 'off_amount', 'off_percent', 'off_upto'),)

    class Meta:
        model = Item
        fields = ['id', 'product', 'offer', 'bought_qty', ]


class CartItemListSerializer(DynamicFieldsModelSerializer):
    items = ItemSerializer(many=True, read_only=True, )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'active', 'created', 'modified']


class CartCreateOrUpdateSeriralizer(DynamicFieldsModelSerializer):
    product = serializers.IntegerField(
        write_only=True,
    )
    offer = serializers.IntegerField(
        write_only=True,
        default=None
    )
    bought_qty = serializers.IntegerField(
        write_only=True,
    )

    class Meta:
        model = Cart
        fields = ['product', 'offer', 'bought_qty', ]

    def create(self, validated_data, *args, **kwargs):
        if not self.context or not self.context['request']:
            raise serializers.ValidationError({
                'errors': ['context must be passed with request as key and request object as a value']
            })

        cart = Cart.objects.create(user=self.context['request'].user)
        try:
            validated_data['product'] = Product.objects.get(
                id=validated_data.get('product'))
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'errors': ['Product does not exist.']
            })
        try:
            offer_id = validated_data.get('offer', None)
            if offer_id:
                validated_data['offer'] = validated_data['product'].offers.get(
                    id=offer_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'errors': ['Offer does not exist or not applicable for this product.']
            })
        new_item = Item.objects.create(cart=cart, **validated_data)
        return cart

    def update(self, instance, validated_data, *args, **kwargs):
        # NOTE: for removing item make seprate api-url.
        product_id = validated_data.pop('product')
        offer_id = validated_data.pop('offer', None)

        try:
            validated_data['product'] = Product.objects.get(id=product_id)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'errors': ['Product does not exist.']
            })

        try:
            if offer_id:
                validated_data['offer'] = validated_data['product'].offers.get(
                    id=offer_id)
            else:
                validated_data['offer'] = None
        except ObjectDoesNotExist:
            raise serializers.ValidationError({
                'errors': ['Offer does not exist or not applicable for this product.']
            })

        validated_data['cart'] = instance
        item = Item.objects.update_or_create(
            cart=instance, product__id=product_id,
            defaults=validated_data
        )
        instance.save()
        return instance
