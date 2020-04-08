from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import User

import uuid, hashlib, datetime, re

from inspector import settings
from .helper_functions import validate_name, unsigned, hash_address

class Listing(models.Model):
    def upload_path(self):
        return 'userimages/listings/{}'.format(self.seller.username)
    TYPE_CHOICES = (
        ('SELL', _('Selling')),
        ('BUY', _('Buying'))
    )

    title = models.CharField(max_length=140)
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    thumbnail = models.ImageField(upload_to=upload_path, default='thumbnail.jpg')
    images = models.ManyToManyField('UploadedImage')
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='SELL')
    price = models.DecimalField(max_digits=10, decimal_places=2,
        validators=[unsigned])
    description = models.TextField()
    address = models.ForeignKey('Address', on_delete=models.PROTECT)
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(null=True)
    contact = models.ForeignKey('Contact', on_delete=models.PROTECT)
    archived = models.BooleanField(default=False)
    last_bumped = models.DateTimeField(default=datetime.datetime(1970, 12, 1, 12, 0))

    def __str__(self):
        return '{} | {}'.format(self.type, self.title)

class ListingView(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(protocol='IPv4')

class Seller(models.Model):
    connected_user = models.OneToOneField(User, on_delete=models.CASCADE,
        primary_key=True)
    full_name = models.CharField(max_length=100, validators=[validate_name])
    show_name = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=30)
    rating = models.PositiveIntegerField(default=3, editable=False)
    avatar = models.ImageField(upload_to='userimages/sellers',
        default='files/userimages/avatar.gif', blank=True)
    mobile_phone = models.CharField(max_length=20,
        validators=[RegexValidator(regex='\+\d{9,18}',
            message='Incorrect number format', code='number_format_incorrect')])
    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.username + "(" + self.mobile_phone + ")"

class Contact(models.Model):
    seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # Format: {"velcom":"+375295151515","mts":"+375332901018"} (max. 4)
    phone_numbers = models.CharField(max_length=150,
        validators=[RegexValidator(regex='{("\w+":"\+*\d+",){,3}("\w+":"\+*\d+"){1}}',
            message='Incorrect format', code='phone_format_incorrect')])
    call_time = models.CharField(max_length=11, default='00:00-23:59')
    # Format: {"vk":"id6053121","telegram":"@sellerigor"} (max. 4)
    social_contacts = models.CharField(max_length=500, default='{}',
        validators=[RegexValidator(regex='{("\w+":"\S+?",){,3}("\w+":"\S+?"){,1}}',
            message='Incorrect format', code='social_format_incorrect')])
    # Format: email@mail.ru,email@gmail.com (max. 2)
    contact_emails = models.CharField(max_length=500, blank=True, null=True,
        validators=[RegexValidator(regex='(\w+?@\w+?\.\w{2,3},){,2}',
            message='Incorrect format', code='emails_format_incorrect')])

    def __str__(self):
        return self.name

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
        editable=False)
    hash = models.CharField(max_length=32, unique=True, editable=False)
    town = models.CharField(max_length=40)
    district = models.CharField(max_length=30, null=True, blank=True)
    street_name = models.CharField(max_length=50, null=True, blank=True)
    house_number = models.CharField(max_length=7, null=True, blank=True)
    apartment = models.PositiveIntegerField(null=True, blank=True)
    postcode = models.CharField(max_length=8, null=True, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=5, editable=False,
        null=True)
    lng = models.DecimalField(max_digits=9, decimal_places=5, editable=False,
        null=True)

    def save(self, *args, **kwargs):
        self.hash = hash_address(self)
        super().save(*args, **kwargs)

    def __str__(self):
        town = self.town if self.town else ''
        district = self.district if self.district else ''
        street = self.street_name if self.street_name else ''
        house = self.house_number if self.house_number else ''
        apartment = self.apartment if self.apartment else ''

        if district or street:
            full_address = '{}, {}, {}, {}, {}'.format(street, house, apartment, district, town)
            full_address = re.sub(r'(, )+', ', ', full_address)
            full_address = re.sub(r'^, ', '', full_address)
        else:
            full_address = town
        return full_address

class Review(models.Model):
    target_seller = models.ForeignKey('Seller', on_delete=models.CASCADE)
    username = models.CharField(max_length=30)
    rating = models.PositiveIntegerField(validators=[
        MinValueValidator(settings.MIN_RATING), MaxValueValidator(settings.MAX_RATING)])
    text = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    additional_text = models.CharField(max_length=150, blank=True, null=True)
    date_edited = models.DateTimeField(null=True)

    def __str__(self):
        return '{} - {}'.format(self.username, self.rating)

class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=80, blank=True, null=True)
    thumbnail = models.ImageField(upload_to='userimages/listings/%d%m%y/thumbnails',
        null=True)
    file = models.ImageField(upload_to='userimages/listings/%d%m%y')
    uploaded = models.DateTimeField(auto_now=True)

    def __str__(self):
        return file
