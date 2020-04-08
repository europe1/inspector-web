from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Listing, Address, UploadedImage

class CreateListingForm(forms.Form):
    TYPE_CHOICES = (
        ('SELL', _('Selling')),
        ('BUY', _('Buying'))
    )

    title = forms.CharField(label=_('Title'))
    type = forms.ChoiceField(label=_('Type'), choices=TYPE_CHOICES)
    price = forms.DecimalField(label=_('Price'), decimal_places=2)
    images = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}),
        required=False)
    description = forms.CharField(label=_('Description'), widget=forms.Textarea)

class ContactForm(forms.Form):
    contact_name = forms.CharField(label=_('Name'))

    phone_operator1 = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Operator')}))
    phone_number1 = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Phone number')}))

    phone_operator2 = forms.CharField(required=False)
    phone_number2 = forms.CharField(required=False)

    phone_operator3 = forms.CharField(required=False)
    phone_number3 = forms.CharField(required=False)

    phone_operator4 = forms.CharField(required=False)
    phone_number4 = forms.CharField(required=False)

    call_time_start = forms.TimeField(required=False)
    call_time_end = forms.TimeField(required=False)

    social_network1 = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Social network')}))
    social_contact1 = forms.CharField(required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Username')}))

    social_network2 = forms.CharField(required=False)
    social_contact2 = forms.CharField(required=False)

    social_network3 = forms.CharField(required=False)
    social_contact3 = forms.CharField(required=False)

    social_network4 = forms.CharField(required=False)
    social_contact4 = forms.CharField(required=False)

    contact_email1 = forms.CharField(required=False)
    contact_email2 = forms.CharField(required=False)

class AddressForm(forms.Form):
    town = forms.CharField()
    district = forms.CharField(required=False)
    street_name = forms.CharField(required=False)
    house_number = forms.CharField(required=False)
    apartment = forms.IntegerField(required=False)
    postcode = forms.CharField(required=False)

class ReviewForm(forms.Form):
    rating = forms.IntegerField()
    review_text = forms.CharField(widget=forms.Textarea)

class SellerForm(forms.Form):
    seller_username = forms.CharField()
    mobile_phone = forms.CharField()
    avatar = forms.ImageField(required=False)
    full_name = forms.CharField()
    show_name = forms.BooleanField(required=False)

class UserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    repeat_password = forms.CharField(widget=forms.PasswordInput)

class UserLogin(forms.Form):
    login_email = forms.EmailField()
    login_password = forms.CharField(widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False)

class EditListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['price', 'description']
    images = forms.ImageField(widget=forms.FileInput(attrs={'multiple': True}),
        required=False)

class EditAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['id', 'cached_id', 'lat', 'lng']

class ImageForm(forms.Form):
    description = forms.CharField()
    file = forms.ImageField()
