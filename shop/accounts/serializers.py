from .models import (
    User,
    UserProfile,
    UserHistory,
)
from .validators import (
    positive_integers_list_validator,
    atleast_one_field_validator,
)

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from products.models import Product
from products.serializers import ProductSerializer
# from orders.serializers import OrderSerializer


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


class UserSerializer(DynamicFieldsModelSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, instance, *args, **kwargs):
        return Token.objects.get(user=instance).key

    def create(self, validated_data, *args, **kwargs):
        phone = validated_data.get('phone', None)
        password = validated_data.get('password', None)
        email = validated_data.get('email', None)
        is_admin = validated_data.get('is_admin', None)

        user = User.objects.create_user(phone, email, password)
        return user

    class Meta:
        model = User
        fields = ['id', 'phone', 'password',
                  'email', 'created', 'modified', 'token', 'is_admin', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserProfileSerializer(DynamicFieldsModelSerializer):
    # read only fields
    # User Model id, phone, email
    id = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    # rw fields
    email = serializers.SerializerMethodField()
    fav_products = ProductSerializer(fields=('id', 'name', 'primary_image'),
                                     read_only=True,
                                     many=True,)
    is_active = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    orders = serializers.SerializerMethodField()
    # write only fields
    active = serializers.BooleanField(write_only=True, )
    add_fav_products = serializers.JSONField(
        write_only=True,
        default=None,
        validators=[positive_integers_list_validator, ]
    )
    delete_fav_products = serializers.JSONField(
        write_only=True,
        default=None,
        validators=[positive_integers_list_validator, ]
    )
    # updation of password
    password1 = serializers.CharField(write_only=True, )
    password2 = serializers.CharField(write_only=True, )

    def get_email(self, instance, *args, **kwargs):
        return instance.user.email

    def get_phone(self, instance, *args, **kwargs):
        return str(instance.user.phone)

    def get_id(self, instance, *args, **kwargs):
        return instance.user.id

    def get_is_active(self, instance, *args, **kwargs):
        return instance.user.is_active

    def get_is_admin(self, instance, *args, **kwargs):
        return instance.user.is_admin

    def get_orders(self, instance, *args, **kwargs):
        from orders.serializers import OrderSerializer
        return OrderSerializer(instance.user.orders, many=True).data

    def update(self, instance, validated_data, *args, **kwargs):
        atleast_one_field_validator(self.fields, validated_data)
        add_fav_products = validated_data.get('add_fav_products', [])
        delete_fav_products = validated_data.get('delete_fav_products', None)
        avatar = validated_data.get('avatar', None)

        instance.user.email = validated_data.get('email', instance.user.email)
        instance.full_name = validated_data.get(
            'full_name', instance.full_name)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birth_date = validated_data.get(
            'birth_date', instance.birth_date)
        instance.last_lat = validated_data.get('last_lat', instance.last_lat)
        instance.last_lon = validated_data.get('last_lon', instance.last_lon)
        instance.purchased_amount = validated_data.get(
            'purchased_amount', instance.purchased_amount)
        instance.address1 = validated_data.get('address1', instance.address1)
        instance.address2 = validated_data.get('address2', instance.address2)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.city = validated_data.get('city', instance.city)
        instance.country = validated_data.get('country', instance.country)
        instance.instagram = validated_data.get(
            'instagram', instance.instagram)
        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.twitter = validated_data.get('twitter', instance.twitter)

        # changes made on 29-04-2020 start
        instance.user.is_admin = validated_data.get(
            'is_admin', instance.user.is_admin)
        instance.user.is_active = validated_data.get(
            'active', instance.user.is_active)
        # changes made on 29-04-2020 end

        if avatar:
            instance.avatar.delete(save=False)
            instance.avatar = avatar
        if add_fav_products:
            fav_products = Product.objects.filter(id__in=add_fav_products)
            instance.fav_products.add(*fav_products)
        if delete_fav_products:
            favs = Product.objects.filter(id__in=delete_fav_products)
            instance.fav_products.remove(*favs)
        instance.save()
        return instance

    class Meta:
        model = UserProfile
        extra_kwargs = {
            'fav_products': {'read_only': True}
        }
        exclude = ['user', ]


class UserHistorySerializer(DynamicFieldsModelSerializer):
    user = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    def get_user(self, instance, *args, **kwargs):
        return UserProfileSerializer(instance.user.profile, fields=('id', 'full_name', 'avatar', )).data

    def get_product(self, instance, *args, **kwargs):
        return ProductSerializer(instance.product, fields=('id', 'name', 'primary_image')).data

    class Meta:
        model = UserHistory
        fields = '__all__'
        # exclude = ['user', ]
