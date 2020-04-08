from inspector import settings

from PIL import Image, ImageFilter

import re, hashlib, requests, os

def geocode(location):
    url = "https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyDNYFzufFNdmzKAtT0sixE6l-FC_LqhrqQ"
    params = {'address': location}

    r = requests.get(url=url, params=params)
    data = r.json()
    # 5 decimal places for ~1m precision
    lat = round(data['results'][0]['geometry']['location']['lat'], 5)
    lng = round(data['results'][0]['geometry']['location']['lng'], 5)
    return [lat, lng]

def star_rating(review):
    star_rating = ''
    for star in range(review.rating):
        star_rating += settings.STAR_SYMBOL
    # Add empty symbols if rating is less than max
    for empty_star in range(settings.MAX_RATING - review.rating):
        star_rating += settings.EMPTY_STAR_SYMBOL
    review.stars = star_rating

def identical_address(adr1, adr2):
    name = adr1.name == adr2.name
    phone_nums = contact1.phone_numbers == contact2.phone_numbers
    soc_contacts = contact1.social_contacts == contact2.social_contacts
    emails = contact1.contact_emails == contact2.contact_emails
    return (name and phone_nums and soc_contacts and emails);

# Get the address cache to check for collision
def hash_address(adr):
    hash = hashlib.sha256()
    hash.update(adr.__str__().encode('utf-8'))
    return hash.hexdigest()

def make_dict(keys, values, key_required):
    dict = '{'
    for i in range(len(keys)):
        if (not key_required and values[i]) or (key_required and keys[i] and values[i]):
            if i != 0:
                dict += ','
            if keys[i]:
                key = keys[i]
            else:
                key = 'null'
            dict += '"{}":"{}"'.format(key, values[i])
    dict += '}'
    return dict

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Validators for listings.models
def unsigned(value):
    if value < 0:
        raise ValidationError(
            _('%(value)s must bigger or equal to 0'),
            params = {'value': value}
        )

def validate_name(full_name):
    name_split = full_name.strip().split(' ');
    if len(name_split) == 3:
        for name in name_split:
            if len(name) < 2:
                raise ValidationError(
                    _('%(value)s is too short'),
                    params = {'value': name}
                )
    else:
        raise ValidationError(
            _('"%(value)s" is invalid name'),
            params = {'value': full_name}
        )

def resize_image(image_path, base=settings.DEFAULT_AVATAR_HEIGHT, ratio=1.618,
    scale=False):
    img = Image.open(image_path)
    height = img.height
    width = img.width
    max = int(base * ratio)

    current_size = height * width
    max_size = max * base
    if (not scale) and (current_size <= max_size):
        return

    if width >= height:
        w = max
        h = base
        check_height = int(height * ratio)
        if check_height < width:
            adjust_width = check_height
            adjust_height = height
        elif check_height > width:
            adjust_width = width
            adjust_height = int(height / ratio)
    elif width < height:
        w = base
        h = max
        check_width = int(width * ratio)
        if check_width < height:
            adjust_width = width
            adjust_height = check_width
        elif check_width > height:
            adjust_width = int(height / ratio)
            adjust_height = height

    padding_x = int((width - adjust_width) * 0.5)
    padding_y = int((height - adjust_height) * 0.5)
    img = img.crop((padding_x, padding_y, img.width - padding_x, img.height - padding_y))
    img = img.resize((w, h))

    # Blur image if it was too big to prevent excess sharpness
    if current_size > max_size * 3:
        img = img.filter(ImageFilter.BoxBlur(0.2))

    img.save(image_path)
