from rest_framework import serializers

from django.core.exceptions import ObjectDoesNotExist
import json

from products.models import (
    Product,
    ProductCategory,
    ProductImage,
    Offer,
    OfferImage,
    Manufacturer,)

from .validators import (
    positive_integers_list_validator,
    more_images_and_rank_validator,
    atleast_one_field_validator
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


class ProductCategorySerializer(DynamicFieldsModelSerializer):
    sub_categories = serializers.JSONField(
        required=True, )

    def create(self, validated_data, *args, **kwargs):
        sub_categories = validated_data.pop('sub_categories', None)
        validated_data['raw_sub_categories'] = json.dumps(sub_categories)
        category = ProductCategory.objects.create(**validated_data)
        category.save()
        return category

    def update(self, instance, validated_data, *args, **kwargs):
        atleast_one_field_validator(
            self.fields, validated_data, *args, **kwargs)
        instance.name = validated_data.get('name', instance.name)
        instance.active = validated_data.get('active', instance.active)
        sub_categories = validated_data.get('sub_categories', None)
        if sub_categories:
            instance.raw_sub_categories = json.dumps(sub_categories)
# check if 'image' key is exist or not (its value may be None there for check for key directly)
        image = validated_data.get('image', None)
        if image:
            # clear image from memory
            instance.image.delete(save=False)
            instance.image = image
        instance.save()
        return instance

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'image', 'active',
                  'created', 'sub_categories']
        extra_kwargs = {
            'active': {'default': True, },
            # 'image': {'allow_empty_file': True}
        }


class ManufacturerSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'
        extra_kwargs = {
            'active': {'default': True, }
        }

    def update(self, instance, validated_data, *args, **kwargs):
        atleast_one_field_validator(
            self.fields, validated_data, *args, **kwargs)
        return super(ManufacturerSerializer, self).update(instance, validated_data, *args, **kwargs)


class OfferImageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = OfferImage
        fields = '__all__'
        extra_kwargs = {
            'active': {'default': True, }
        }


class OfferSerializer(DynamicFieldsModelSerializer):
    # read only fields
    images = serializers.SerializerMethodField(read_only=True, )
    products = serializers.SerializerMethodField(read_only=True, )
# write only fields
    add_images_rank = serializers.JSONField(
        write_only=True,
        default=None,
        validators=(positive_integers_list_validator, )
    )

    add_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        default=None,
    )

    delete_images = serializers.JSONField(
        write_only=True,
        default=None,
        validators=(positive_integers_list_validator, )
    )

    def get_products(self, instance, *args, **kwargs, ):
        return [{'id': product.id, 'name': product.name}for product in instance.products.all()]

    def get_images(self, instance, *args, **kwargs):
        query_set = instance.more_images.all().order_by('rank')
        return OfferImageSerializer(query_set, many=True, fields=('id', 'image', 'rank')).data

    def validate(self, data, *args, **kwargs):
        return more_images_and_rank_validator(data, *args, **kwargs)

    def create(self, validated_data, *args, **kwargs):
        more_images = validated_data.pop('add_images', None)
        more_images_rank = validated_data.pop('add_images_rank', None)
        _ = validated_data.pop('delete_images', None)
        offer = Offer.objects.create(**validated_data)
        offer.save()
        if more_images:
            data = []
            for i, image in enumerate(more_images):
                offer_image_data = dict()
                offer_image_data['image'] = image
                offer_image_data['offer'] = offer.id
                offer_image_data['rank'] = more_images_rank[i]
                data.append(offer_image_data)
            offer_image_serializer = OfferImageSerializer(data=data, many=True)
            if offer_image_serializer.is_valid():
                offer_image_serializer.save()
            else:
                raise serializers.ValidationError({
                    'errors': offer_image_serializer.errors
                })
        return offer

    def update(self, instance, validated_data, *args, **kwargs):
        atleast_one_field_validator(
            self.fields, validated_data, *args, **kwargs)

        instance.name = validated_data.get('name', instance.name)
        instance.start = validated_data.get('start', instance.start)
        instance.end = validated_data.get('end', instance.end)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.given_by = validated_data.get('given_by', instance.given_by)
        instance.min_qty = validated_data.get('min_qty', instance.min_qty)
        instance.min_amount = validated_data.get(
            'min_amount', instance.min_amount)
        instance.off_amount = validated_data.get(
            'off_amount', instance.off_amount)
        instance.off_percent = validated_data.get(
            'off_percent', instance.off_percent)
        instance.off_upto = validated_data.get('off_upto', instance.off_upto)
        instance.tnc = validated_data.get('tnc', instance.tnc)
        instance.active = validated_data.get('active', instance.active)
        instance.save()
# delete existing images if any (if found otherwise ignore)
        delete_images_id = validated_data.get('delete_images', None)
        if delete_images_id:
            for image_id in delete_images_id:
                try:
                    offer_image = OfferImage.objects.get(id=image_id)
                    # clear image from memory
                    offer_image.image.delete(save=False)
                    offer_image.delete()
                except:
                    continue
# add new images if any
        more_images = validated_data.get('add_images', None)
        more_images_rank = validated_data.get('add_images_rank', None)
        if more_images:
            data = []
            for i, image in enumerate(more_images):
                offer_image_data = dict()
                offer_image_data['image'] = image
                offer_image_data['offer'] = instance.id
                offer_image_data['rank'] = more_images_rank[i]
                data.append(offer_image_data)
            offer_image_serializer = OfferImageSerializer(data=data, many=True)
            if offer_image_serializer.is_valid():
                offer_image_serializer.save()
            else:
                raise serializers.ValidationError({
                    'errors': offer_image_serializer.errors
                })
        return instance

    class Meta:
        model = Offer
        fields = '__all__'
        extra_kwargs = {
            'active': {'default': True, },
        }


class ProductImageSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'
        extra_kwargs = {
            'active': {'default': True},
        }


class ProductSerializer(DynamicFieldsModelSerializer):
    # read only fields
    images = serializers.SerializerMethodField(read_only=True, )
    category = ProductCategorySerializer(
        fields=('id', 'name', ), read_only=True, )
    manufacturer = ManufacturerSerializer(
        fields=('id', 'name'), read_only=True, )
    offers = OfferSerializer(many=True, read_only=True,
                             fields=('id', 'images', 'name', 'start',
                                     'end', 'given_by', 'active', 'off_amount',
                                     'off_percent', 'off_upto', 'min_amount', 'min_qty',))
    likes = serializers.SerializerMethodField()
# write only fields
    add_category = serializers.IntegerField(write_only=True,)
    add_offers = serializers.JSONField(write_only=True, default=None, )
    add_manufacturer = serializers.IntegerField(write_only=True, )
    add_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        default=None,
    )
    add_images_rank = serializers.JSONField(
        write_only=True,
        default=None,
        validators=(positive_integers_list_validator, )
    )
    delete_images = serializers.JSONField(
        write_only=True,
        default=None,
        validators=(positive_integers_list_validator, )
    )
    remove_offers = serializers.JSONField(
        write_only=True,
        default=None,
        validators=(positive_integers_list_validator, )
    )

    def to_internal_value(self, data, *args, **kwargs, ):
        # print('products\\serializers.py:', 'to_internal_value')
        return super(ProductSerializer, self).to_internal_value(data, *args, **kwargs)

    def to_representation(self, instance, *args, **kwargs):
        # print('products\\serializers.py:', 'to_representaion', )
        if self.context.get('product_viewed', None):
            _ = Product.objects.filter(id=instance.id).update(
                total_views=instance.total_views+1
            )
            instance.total_views += 1
        return super(ProductSerializer, self).to_representation(instance, *args, **kwargs)

    def get_likes(self, instance, *args, **kwargs):
        return instance.liked_by.count()

    def get_images(self, instance, *args, **kwargs):
        query_set = instance.more_images.all().order_by('rank')
        return ProductImageSerializer(query_set, many=True, fields=('id', 'image', 'rank', )).data

    def validate(self, data, *args, **kwargs):
        return more_images_and_rank_validator(data, *args, **kwargs)

    def create(self, validated_data, *args, **kwargs):
        offers_id = validated_data.pop('add_offers', None)
        manufacturer_id = validated_data.pop('add_manufacturer', None)
        category_id = validated_data.pop('add_category', None)
        more_images = validated_data.pop('add_images', None)
        more_images_rank = validated_data.pop('add_images_rank', None)
# Not required field for creation of new products
        _ = validated_data.pop('remove_offers', None)
        _ = validated_data.pop('delete_images', None)

        offers, manufacturer, category, errors = [], None, None, {}
        if offers_id:
            offers = Offer.objects.filter(id__in=offers_id)
        try:
            manufacturer = Manufacturer.objects.get(id=manufacturer_id)
        except:
            errors['manufacturer'] = ['Does not exist.']
        try:
            category = ProductCategory.objects.get(id=category_id)
        except:
            errors['category'] = ['Does not exist.']
# CHECK for any error till now
        if errors:
            raise serializers.ValidationError({
                'errors': errors
            })
        product = Product.objects.create(**validated_data)
        product.manufacturer = manufacturer
        product.category = category
        product.offers.add(*offers)
        product.save()
        if more_images:
            data = []
            for i, image in enumerate(more_images):
                product_image_data = dict()
                product_image_data['image'] = image
                product_image_data['product'] = product.id
                product_image_data['rank'] = more_images_rank[i]
                data.append(product_image_data)
            product_image_serializer = ProductImageSerializer(
                data=data, many=True, )
            if product_image_serializer.is_valid():
                product_image_serializer.save()
            else:
                raise serializers.ValidationError({
                    'errors': product_image_serializer.errors
                })
        return product

    def update(self, instance, validated_data, *args, **kwargs):
        atleast_one_field_validator(
            self.fields, validated_data, *args, **kwargs)
        errors = {}
# update basic fields
        instance.name = validated_data.get('name', instance.name)
        instance.sub_category = validated_data.get(
            'sub_category', instance.sub_category)
        instance.features = validated_data.get('features', instance.features)
        instance.ingredients = validated_data.get(
            'ingredients', instance.ingredients)
        instance.total_sold = validated_data.get(
            'total_sold', instance.total_sold)
        instance.total_left = validated_data.get(
            'total_left', instance.total_left)
        instance.limits = validated_data.get('limits', instance.limits)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.mrp = validated_data.get('mrp', instance.mrp)
        instance.price = validated_data.get('price', instance.price)
        instance.nos = validated_data.get('nos', instance.nos)
        instance.qty = validated_data.get('qty', instance.qty)
        instance.qty_unit = validated_data.get('qty_unit', instance.qty_unit)
        instance.best_before = validated_data.get(
            'best_before', instance.best_before)
        instance.active = validated_data.get('active', instance.active)
# update category
        category_id = validated_data.get('add_category', None)
        if category_id:
            try:
                category = ProductCategory.objects.get(id=category_id)
                instance.category = category
            except:
                errors['category'] = ['Does not exist.']
# update primary_image
        primary_image = validated_data.get('primary_image', None)
        if primary_image:
            instance.primary_image.delete(save=False)
            instance.primary_image = primary_image
# update manufacturer
        manufacturer_id = validated_data.get('add_manufacturer', None)
        if manufacturer_id:
            try:
                manufacturer = Manufacturer.objects.get(id=manufacturer_id)
                instance.manufacturer = manufacturer
            except:
                errors['manufacturer'] = ['Does not exist.']
        if errors:
            raise serializers.ValidationError({
                'errors': errors
            })
# delete old images
        delete_images_id = validated_data.get('delete_images', None)
        if delete_images_id:
            for image_id in delete_images_id:
                try:
                    product_image = ProductImage.objects.get(id=image_id)
                    # clear image from memory
                    product_image.image.delete(save=False)
                    product_image.delete()
                except:
                    continue
# add new images with rank
        more_images = validated_data.get('add_images', None)
        more_images_rank = validated_data.get('add_images_rank', None)
        if more_images:
            data = []
            for i, image in enumerate(more_images):
                product_image_data = dict()
                product_image_data['image'] = image
                product_image_data['product'] = instance.id
                product_image_data['rank'] = more_images_rank[i]
                data.append(product_image_data)
            product_image_serializer = ProductImageSerializer(
                data=data, many=True, )
            if product_image_serializer.is_valid():
                product_image_serializer.save()
            else:
                raise serializers.ValidationError({
                    'errors': product_image_serializer.errors
                })
# delete old offers
        delete_offers_id = validated_data.get('remove_offers', None)
        if delete_offers_id:
            for _id in delete_offers_id:
                try:
                    offer = Offer.objects.get(id=_id)
                    instance.offers.remove(offer)
                except:
                    pass
# add new offers
        offers_id = validated_data.get('add_offers', None)
        offers = []
        if offers_id:
            offers = Offer.objects.filter(id__in=offers_id)
        instance.offers.add(*offers)
        instance.save()
        return instance

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'active': {'default': True},
            'total_views': {'read_only': True}
        }
