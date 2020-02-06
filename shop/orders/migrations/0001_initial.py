# Generated by Django 3.0.1 on 2020-01-24 16:00

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FreezeProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freeze_mrp', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Producr Mrp')),
                ('freeze_price', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Producr Price ')),
                ('freeze_nos', models.PositiveIntegerField(default=1, verbose_name='No of pieces')),
                ('freeze_qty', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Weight or Volume Magnitude')),
                ('freeze_qty_unit', models.CharField(choices=[('Kg', 'Kilogram'), ('g', 'Gram'), ('L', 'Liter'), ('mL', 'Milliliter'), ('m', 'Meter'), ('cm', 'Centimeter')], max_length=10, verbose_name='Quantity unit(Kg, mL ETC)')),
                ('bought_qty', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Multiple of nos, customer bought')),
                ('discount', models.DecimalField(decimal_places=4, default=0.0, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Discount on product after offers applied')),
                ('total_amount', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Amount of total Quantity of this product with discount.')),
                ('created', models.DateTimeField(editable=False, verbose_name='Product creation date')),
                ('applied_offer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='freeze_products', to='products.Offer')),
                ('original', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='freeze_products', to='products.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('saved', 'SAVED'), ('pending', 'PENDING'), ('completed', 'COMPLETED'), ('cancelled_by_user', 'CANCELLED_BY_USER'), ('cancelled_by_store', 'CANCELLED_BY_STORE')], default='saved', max_length=20, verbose_name='Order Status')),
                ('favourite', models.BooleanField(default=False, verbose_name='Is order is favourite')),
                ('delivered_date', models.CharField(max_length=40, null=True, verbose_name='Order Delivered date')),
                ('amt_by_price', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Total sum of products price')),
                ('amt_by_mrp', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Total sum of products mrp')),
                ('discount_sum', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Total discount via offers on products')),
                ('charges', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Taxes or other charges')),
                ('amount', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='price_sum + charges - discount')),
                ('delivered_by', models.CharField(max_length=60, null=True, verbose_name='Delivery Person')),
                ('order_location', models.TextField(null=True, verbose_name='Address of Ordering place')),
                ('delivery_location', models.TextField(null=True, verbose_name='Address of Delivery place')),
                ('comment', models.TextField(null=True, verbose_name='Comment for order by customer')),
                ('cancel_reason', models.CharField(max_length=100, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('products', models.ManyToManyField(related_name='orders_purchased', to='orders.FreezeProduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raw_details', models.TextField(blank=True, verbose_name='Payment details (JSON)')),
                ('active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(editable=False)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.Order')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bought_qty', models.DecimalField(decimal_places=4, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0'))], verbose_name='Multiple of nos, customer bought')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.Cart')),
                ('offer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_offers', to='products.Offer')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='products.Product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='order',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart', to='orders.Order'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='carts', to=settings.AUTH_USER_MODEL),
        ),
    ]
