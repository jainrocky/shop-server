# Generated by Django 3.0.1 on 2020-01-24 16:00

import accounts.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phone_field.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone', phone_field.models.PhoneField(max_length=31, unique=True, verbose_name='User Phone')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='User Email')),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('created', models.DateTimeField(editable=False, verbose_name='User creation timestamp')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='User last update timestamp')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=60, verbose_name='Full Name')),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], max_length=8, null=True, verbose_name='Gender')),
                ('birth_date', models.CharField(max_length=40, null=True, verbose_name='Date of Birth')),
                ('avatar', models.ImageField(null=True, upload_to=accounts.utils.profile_image_upload_to, verbose_name='Avatar')),
                ('last_lat', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('last_lon', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('purchased_amount', models.DecimalField(decimal_places=4, max_digits=9, null=True)),
                ('address1', models.CharField(max_length=256, null=True, verbose_name='Address line 1')),
                ('address2', models.CharField(max_length=256, null=True, verbose_name='Address line 2')),
                ('zip_code', models.CharField(max_length=12, null=True, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(max_length=128, null=True, verbose_name='City')),
                ('country', models.CharField(max_length=3, null=True, verbose_name='Country')),
                ('instagram', models.CharField(max_length=100, null=True, verbose_name='Instagram Id')),
                ('facebook', models.CharField(max_length=100, null=True, verbose_name='Facebook Id')),
                ('twitter', models.CharField(max_length=100, null=True, verbose_name='Twitter Id')),
                ('created', models.DateTimeField(editable=False, verbose_name='Profile creation timestamp')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='UserProfile last updation timestamp')),
                ('fav_products', models.ManyToManyField(related_name='liked_by', to='products.Product')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField(null=True)),
                ('lat', models.DecimalField(decimal_places=6, max_digits=12, null=True)),
                ('lon', models.DecimalField(decimal_places=6, max_digits=12, null=True)),
                ('created', models.DateTimeField(editable=False)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='histories', to='products.Product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='histories', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
