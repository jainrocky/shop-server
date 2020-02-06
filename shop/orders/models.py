from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
import json

from products.models import (
    Product,
    Offer,
    QTY_UNITS
)

ORDER_STATUS = (
    # CHECK FOR MAX_LENGTH BEFORE ADDING NEW CHOICES
    ('saved', 'SAVED'),
    ('pending', 'PENDING'),
    ('completed', 'COMPLETED'),
    ('cancelled_by_user', 'CANCELLED_BY_USER'),
    ('cancelled_by_store', 'CANCELLED_BY_STORE'),
)


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20, verbose_name='Order Status',
        choices=ORDER_STATUS, default='saved')
    products = models.ManyToManyField(
        to='FreezeProduct',
        related_name='orders_purchased',
    )
    favourite = models.BooleanField(
        default=False, verbose_name='Is order is favourite', )
    delivered_date = models.CharField(
        max_length=40, verbose_name='Order Delivered date', null=True)
    amt_by_price = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Total sum of products price',
        validators=[MinValueValidator(Decimal(0.0))])
    amt_by_mrp = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Total sum of products mrp',
        validators=[MinValueValidator(Decimal(0.0))])
    discount_sum = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Total discount via offers on products',
        validators=[MinValueValidator(Decimal(0.0))])
    charges = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Taxes or other charges',
        validators=[MinValueValidator(Decimal(0.0))])
    amount = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='price_sum + charges - discount',
        validators=[MinValueValidator(Decimal(0.0))])
    delivered_by = models.CharField(
        max_length=60, verbose_name='Delivery Person', null=True)
    order_location = models.TextField(
        verbose_name='Address of Ordering place', null=True,)
    delivery_location = models.TextField(
        verbose_name='Address of Delivery place', null=True)
    comment = models.TextField(
        verbose_name='Comment for order by customer', null=True, )
    cancel_reason = models.CharField(max_length=100, null=True,)
    active = models.BooleanField(default=True, )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)+' Status: '+self.status


class Payment(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.SET_NULL, null=True, blank=True, )
    raw_details = models.TextField(
        blank=True, verbose_name='Payment details (JSON)')
    active = models.BooleanField(default=True, )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Payment, self).save(*args, **kwargs)

    @property
    def details(self, ):
        if self.raw_details:
            return json.loads(self.raw_details)
        return None

    def __str__(self):
        return self.details


'''
    State of the Product at the time of Ordering.
'''


class FreezeProduct(models.Model):
    original = models.ForeignKey(
        to=Product,
        related_name='freeze_products',
        on_delete=models.SET_NULL,
        null=True,
    )
    freeze_mrp = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Producr Mrp',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    freeze_price = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Producr Price ',
        validators=[MinValueValidator(Decimal(0.0)), ], )

    freeze_nos = models.PositiveIntegerField(
        default=1, verbose_name='No of pieces', )
    freeze_qty = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Weight or Volume Magnitude',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    freeze_qty_unit = models.CharField(
        max_length=10, verbose_name='Quantity unit(Kg, mL ETC)', choices=QTY_UNITS)
    # add total_units_bought
    bought_qty = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Multiple of nos, customer bought',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    applied_offer = models.ForeignKey(
        to=Offer,
        related_name='freeze_products',
        on_delete=models.SET_NULL,
        null=True,
    )
    discount = models.DecimalField(
        max_digits=12, decimal_places=4,
        verbose_name='Discount on product after offers applied',
        default=0.0,
        validators=[MinValueValidator(Decimal(0.0)), ], )

    total_amount = models.DecimalField(
        max_digits=12, decimal_places=4,
        verbose_name='Amount of total Quantity of this product with discount.',
        validators=[MinValueValidator(Decimal(0.0)), ],
    )

    created = models.DateTimeField(
        editable=False,
        verbose_name='Product creation date', )
    # modified = models.DateTimeField(auto_now=True, )

    def __str__(self):
        if self.original:
            return self.original.name
        return super().__str__()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(FreezeProduct, self).save(*args, **kwargs)


class Item(models.Model):
    product = models.ForeignKey(
        to=Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        null=True,
    )
    bought_qty = models.DecimalField(
        max_digits=12, decimal_places=4, verbose_name='Multiple of nos, customer bought',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    offer = models.ForeignKey(
        to=Offer,
        on_delete=models.SET_NULL,
        related_name='cart_offers',
        null=True,
    )
    cart = models.ForeignKey(
        to='Cart',
        on_delete=models.CASCADE,
        related_name='items'
    )

    def __str__(self, ):
        return '< Item: '+self.product.name+' >'


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts'
    )
    order = models.OneToOneField(
        to=Order,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cart'
    )
    @property
    def items_count(self, *args, **kwargs):
        return self.items.count()

    @property
    def items(self, *args, **kwargs):
        return self.items.all()

    active = models.BooleanField(default=True, )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
