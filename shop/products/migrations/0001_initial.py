# Generated by Django 3.0.1 on 2020-01-24 16:00

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import products.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Manufacturer Name')),
                ('address1', models.CharField(max_length=1024, null=True, verbose_name='Address line 1')),
                ('address2', models.CharField(max_length=1024, null=True, verbose_name='Address line 2')),
                ('zip_code', models.CharField(max_length=12, null=True, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(max_length=1024, null=True, verbose_name='City')),
                ('country', models.CharField(max_length=3, null=True, verbose_name='Country')),
                ('other_details', models.CharField(max_length=100, null=True)),
                ('active', models.BooleanField(default=True, verbose_name='Is Manufacturer active')),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Offer Name or Title')),
                ('start', models.CharField(max_length=40, verbose_name='Offer starts date')),
                ('end', models.CharField(max_length=40, verbose_name='Offer ends date')),
                ('description', models.TextField(null=True, verbose_name='Offer details')),
                ('given_by', models.CharField(choices=[('store', 'Store'), ('paytm', 'Paytm'), ('googlepay', 'Google Pay'), ('phonepe', 'PhonePe'), ('brand', 'Brand')], max_length=40, verbose_name='Offer Given by(brand, store, paytm, ETC)')),
                ('min_qty', models.DecimalField(decimal_places=4, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('max_qty', models.DecimalField(decimal_places=4, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('min_amount', models.DecimalField(decimal_places=4, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('off_amount', models.DecimalField(decimal_places=4, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('off_percent', models.DecimalField(decimal_places=4, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('off_upto', models.DecimalField(decimal_places=4, default=0.0, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('tnc', models.TextField(null=True)),
                ('active', models.BooleanField(default=True, verbose_name='Is Offer active')),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Product Name')),
                ('primary_image', models.ImageField(upload_to=products.utils.primary_image_upload_to, verbose_name='Primary Image')),
                ('sub_category', models.CharField(max_length=60, verbose_name='EG: Salt & Sugar(SELECT FROM category.sub_categories)')),
                ('features', models.TextField(null=True, verbose_name='Product Features')),
                ('ingredients', models.TextField(null=True, verbose_name='Product Ingredients')),
                ('total_sold', models.PositiveIntegerField(default=0, verbose_name='Product Sold Count')),
                ('total_left', models.PositiveIntegerField(default=0, null=True, verbose_name='Product Left in stock')),
                ('limits', models.PositiveIntegerField(default=3, verbose_name='Product limit')),
                ('description', models.TextField(null=True, verbose_name='Product Description')),
                ('mrp', models.DecimalField(decimal_places=4, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Producr Mrp')),
                ('price', models.DecimalField(decimal_places=4, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Producr Price ')),
                ('nos', models.PositiveIntegerField(default=1, verbose_name='No of pieces')),
                ('qty', models.DecimalField(decimal_places=4, max_digits=9, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Weight or Volume Magnitude')),
                ('qty_unit', models.CharField(choices=[('Kg', 'Kilogram'), ('g', 'Gram'), ('L', 'Liter'), ('mL', 'Milliliter'), ('m', 'Meter'), ('cm', 'Centimeter')], max_length=10, verbose_name='Quantity unit(Kg, mL ETC)')),
                ('best_before', models.CharField(max_length=40, null=True, verbose_name='Product max life')),
                ('total_views', models.PositiveIntegerField(default=0)),
                ('active', models.BooleanField(default=True, verbose_name='Is Product active')),
                ('created', models.DateTimeField(editable=False, verbose_name='Product creation date')),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='Product Category')),
                ('raw_sub_categories', models.TextField(verbose_name='SubCategory (JSON)')),
                ('image', models.ImageField(null=True, upload_to=products.utils.category_image_upload_to)),
                ('active', models.BooleanField(default=True, verbose_name='Is category active')),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=products.utils.products_image_upload_to, verbose_name="Product's More images")),
                ('rank', models.PositiveIntegerField(verbose_name='Product Image rank')),
                ('active', models.BooleanField(default=True, verbose_name='Is image active')),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='more_images', to='products.Product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.ProductCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='manufacturer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.Manufacturer'),
        ),
        migrations.AddField(
            model_name='product',
            name='offers',
            field=models.ManyToManyField(related_name='products', to='products.Offer'),
        ),
        migrations.CreateModel(
            name='OfferImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.PositiveIntegerField(verbose_name='Offer Image rank')),
                ('image', models.ImageField(null=True, upload_to=products.utils.offers_image_upload_to)),
                ('active', models.BooleanField(default=True, verbose_name='Is OfferImage active')),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='more_images', to='products.Offer')),
            ],
        ),
    ]
