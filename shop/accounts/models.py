from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from phone_field import PhoneField
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.authtoken.models import Token
import json

from django.core.validators import RegexValidator
from products.models import Product
from .utils import profile_image_upload_to


class UserManager(BaseUserManager):
    def create_user(self, phone, email, password=None):
        if not phone:
            raise ValueError('User must have phone number')
        user = self.model(
            phone=phone,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(self._db)
        return user

    def create_superuser(self, phone, email, password=None):
        user = self.create_user(
            phone,
            email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone = PhoneField(unique=True, verbose_name='User Phone', validators=(RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+919999999999'."),))
    email = models.EmailField(
        verbose_name='User Email', null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created = models.DateTimeField(
        editable=False, verbose_name='User creation timestamp', )
    modified = models.DateTimeField(
        auto_now=True, verbose_name='User last update timestamp')
    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(User, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.phone)

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(
        max_length=60, verbose_name='Full Name', null=True)
    gender = models.CharField(max_length=8, choices=(
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    ), null=True, verbose_name='Gender', blank=True)
    birth_date = models.CharField(
        max_length=40, null=True, verbose_name='Date of Birth')
    avatar = models.ImageField(
        upload_to=profile_image_upload_to,
        verbose_name='Avatar', null=True)
    last_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True)
    last_lon = models.DecimalField(
        max_digits=9, decimal_places=6, null=True)
    fav_products = models.ManyToManyField(
        Product,
        related_name='liked_by', )
    purchased_amount = models.DecimalField(
        max_digits=9, decimal_places=4, null=True)
    address1 = models.CharField(
        "Address line 1",
        max_length=256, null=True
    )
    address2 = models.CharField(
        "Address line 2",
        max_length=256, null=True
    )
    zip_code = models.CharField(
        "ZIP / Postal code",
        max_length=12, null=True
    )
    city = models.CharField(
        "City",
        max_length=128, null=True
    )
    country = models.CharField(
        "Country",
        max_length=3, null=True
    )
    instagram = models.CharField(
        max_length=100, verbose_name='Instagram Id', null=True, )
    facebook = models.CharField(
        max_length=100, verbose_name='Facebook Id', null=True, )
    twitter = models.CharField(
        max_length=100, verbose_name='Twitter Id', null=True, )
    created = models.DateTimeField(
        editable=False, verbose_name='Profile creation timestamp', )
    modified = models.DateTimeField(
        auto_now=True, verbose_name='UserProfile last updation timestamp')

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(UserProfile, self).save(*args, **kwargs)

    # def __str__(self):
    #     return str(self.full_name)+' '+str(self.birth_date)


class UserHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='histories')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name='histories')
    source = models.TextField(null=True, )
    lat = models.DecimalField(max_digits=12, decimal_places=6, null=True)
    lon = models.DecimalField(max_digits=12, decimal_places=6, null=True)
    created = models.DateTimeField(editable=False, )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(UserHistory, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)


# initiate: attach Profile, History, Token
@receiver(post_save, sender=User, dispatch_uid='initiate_new_user')
def initiate_user(sender, instance, created=False, **kwargs):
    user = instance
    if created:
        profile = UserProfile(user=user)
        profile.save()
        # history = UserHistory(user=user)
        # history.save()
        Token.objects.create(user=instance)
