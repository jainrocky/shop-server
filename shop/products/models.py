from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
import json
from .utils import (
    primary_image_upload_to,
    products_image_upload_to,
    offers_image_upload_to,
    category_image_upload_to,

)
QTY_UNITS = (
    ('Kg', 'Kilogram'),
    ('g', 'Gram'),
    ('L', 'Liter'),
    ('mL', 'Milliliter'),
    ('m', 'Meter'),
    ('cm', 'Centimeter'),
)

OFFER_GIVEN_BY = (
    ('store', 'Store'),
    ('paytm', 'Paytm'),
    ('googlepay', 'Google Pay'),
    ('phonepe', 'PhonePe'),
    ('brand', 'Brand'),
)


class Product(models.Model):
    name = models.TextField(verbose_name='Product Name', )
    primary_image = models.ImageField(
        upload_to=primary_image_upload_to, verbose_name='Primary Image', )
    category = models.ForeignKey(
        'ProductCategory', on_delete=models.SET_NULL, related_name='products', null=True, )
    sub_category = models.CharField(
        max_length=60, verbose_name='EG: Salt & Sugar(SELECT FROM category.sub_categories)',
    )
    features = models.TextField(
        verbose_name='Product Features', null=True, )
    ingredients = models.TextField(
        verbose_name='Product Ingredients', null=True, )
    total_sold = models.PositiveIntegerField(
        default=0, verbose_name='Product Sold Count', )
    total_left = models.PositiveIntegerField(
        default=0, verbose_name='Product Left in stock', null=True, )
    # NOTE: Default limit is 3
    limits = models.PositiveIntegerField(
        default=3, verbose_name='Product limit', )
    description = models.TextField(
        verbose_name='Product Description', null=True, )
    mrp = models.DecimalField(
        max_digits=9, decimal_places=4, verbose_name='Producr Mrp',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    price = models.DecimalField(
        max_digits=9, decimal_places=4, verbose_name='Producr Price ',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    nos = models.PositiveIntegerField(default=1, verbose_name='No of pieces', )
    qty = models.DecimalField(
        max_digits=9, decimal_places=4, verbose_name='Weight or Volume Magnitude',
        validators=[MinValueValidator(Decimal(0.0)), ], )
    qty_unit = models.CharField(
        max_length=10, verbose_name='Quantity unit(Kg, mL ETC)', choices=QTY_UNITS)
    best_before = models.CharField(
        max_length=40, null=True, verbose_name='Product max life', )
    manufacturer = models.ForeignKey(
        'Manufacturer', on_delete=models.SET_NULL, null=True,  related_name='products', )
    offers = models.ManyToManyField(
        'Offer', related_name='products', )
    total_views = models.PositiveIntegerField(default=0,)
    active = models.BooleanField(
        verbose_name='Is Product active', default=True, )
    created = models.DateTimeField(
        editable=False, verbose_name='Product creation date', )
    modified = models.DateTimeField(auto_now=True, )

    @property
    def images(self, ):
        return self.more_images.all()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Product, self).save(*args, **kwargs)


class ProductCategory(models.Model):
    name = models.TextField(
        verbose_name='Product Category', )
    '''
        sub_category : [
            'category-1',
            'category-2',
            ...
            'category-n',
        ]
    '''
    raw_sub_categories = models.TextField(
        verbose_name='SubCategory (JSON)', )
    image = models.ImageField(
        upload_to=category_image_upload_to, null=True,)

    active = models.BooleanField(
        default=True, verbose_name='Is category active', )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    @property
    def sub_categories(self, ):
        print('Tag: ProductCategoryModel',
              'Running sub_categories function property')
        if self.raw_sub_categories:
            return json.loads(self.raw_sub_categories)
        return None

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(ProductCategory, self).save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='more_images',)
    image = models.ImageField(
        upload_to=products_image_upload_to, verbose_name='Product\'s More images', )
    rank = models.PositiveIntegerField(verbose_name='Product Image rank', )
    active = models.BooleanField(
        default=True, verbose_name='Is image active', )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def __str__(self):
        return str(self.image.url)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(ProductImage, self).save(*args, **kwargs)


class Manufacturer(models.Model):
    name = models.TextField(verbose_name='Manufacturer Name', )
    address1 = models.CharField(
        "Address line 1",
        max_length=1024, null=True,
    )
    address2 = models.CharField(
        "Address line 2",
        max_length=1024, null=True,
    )
    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12, null=True,
    )
    city = models.CharField(
        "City",
        max_length=1024, null=True,
    )
    country = models.CharField(
        "Country",
        max_length=3, null=True,
    )
    other_details = models.CharField(max_length=100, null=True, )

    active = models.BooleanField(
        default=True, verbose_name='Is Manufacturer active', )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Manufacturer, self).save(*args, **kwargs)


class Offer(models.Model):
    name = models.TextField(verbose_name='Offer Name or Title', )
    start = models.CharField(max_length=40,
                             verbose_name='Offer starts date', )
    end = models.CharField(
        max_length=40, verbose_name='Offer ends date')
    description = models.TextField(
        verbose_name='Offer details', null=True, )
    given_by = models.CharField(
        max_length=40, verbose_name='Offer Given by(brand, store, paytm, ETC)',
        choices=OFFER_GIVEN_BY,
    )

    min_qty = models.DecimalField(
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
        null=True,
    )
    max_qty = models.DecimalField(
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
        null=True,
    )
    # min amount for offer to be applicable
    min_amount = models.DecimalField(
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
        null=True,
    )
    # off amount in term of rupees
    off_amount = models.DecimalField(
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
        null=True,
    )
    # off amount in terms of percent
    off_percent = models.DecimalField(
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
        null=True,
    )
    # max ruppes to be off on a product
    # NOTE: if product is not for off than it has zero off_upto
    off_upto = models.DecimalField(
        default=0.0,
        max_digits=9, decimal_places=4,
        validators=[MinValueValidator(Decimal(0.0)), ],
    )
    # offer's TnC
    tnc = models.TextField(null=True, )
    active = models.BooleanField(
        default=True, verbose_name='Is Offer active', )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    @property
    def images(self, ):
        return self.objects.images.all()

    @property
    def products(self, ):
        return self.objects.products.all()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Offer, self).save(*args, **kwargs)


class OfferImage(models.Model):
    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='more_images',)
    rank = models.PositiveIntegerField(verbose_name='Offer Image rank', )
    image = models.ImageField(
        upload_to=offers_image_upload_to, null=True, )
    active = models.BooleanField(
        default=True, verbose_name='Is OfferImage active', )
    created = models.DateTimeField(editable=False, )
    modified = models.DateTimeField(auto_now=True, )

    def __str__(self):
        return str(self.image.url)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(OfferImage, self).save(*args, **kwargs)
