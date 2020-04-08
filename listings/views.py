from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.utils import timezone, html

import ast, re

from .helper_functions import *
from countries import locale_checks
from .models import *
from .forms import *
from inspector import settings

def user_register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            ok = True

            email = user_form.cleaned_data['email']
            if not re.fullmatch('[a-zA-Z0-9._]+@\w+.\w{2,3}', email):
                user_form.add_error('email', _('Email is incorrect'))
                ok = False

            password = user_form.cleaned_data['password']
            if len(password) < 6:
                user_form.add_error('password',
                    _('The password must be at least 6 characters long'))
                ok = False
            if password != user_form.cleaned_data['repeat_password']:
                user_form.add_error('repeat_password',
                    _('Passwords do not match'))
                ok = False

            if ok:
                if ('gmail' in email.split('@')[1]):
                    username = email.split('@')[0].replace('.', '')
                else:
                    username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    user_form.add_error('email', _('Such user already exists'))
                else:
                    new_user = User.objects.create_user(username, email, password)
                    new_user.save()
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('index'))
    else:
        user_form = UserForm()
    return render(request, 'listings/user.htm', {'user_form': user_form})

def user_login(request):
    login_form = UserLogin()
    return render(request, 'listings/login.htm', {'login_form': login_form})

def index(request):
    page = request.GET.get('p')
    if page:
        try:
            page = int(page)
            entries = page * settings.ENTRIES_PER_PAGE
            start_index = entries - settings.ENTRIES_PER_PAGE
        except ValueError:
            page = 1
            start_index = 0
            entries = settings.ENTRIES_PER_PAGE
    else:
        page = 1
        start_index = 0
        entries = settings.ENTRIES_PER_PAGE

    allowed_filters = ['title', '-title', 'price', '-price', 'date_added']
    sort = request.GET.get('sort')
    if not sort in allowed_filters:
        sort = '-date_added'

    search = request.GET.get('search')
    if search:
        search = html.escape(search)
        all_listings = Listing.objects.filter(
                archived=False, title__contains=search
            ).order_by('-last_bumped', sort)[start_index:entries]
    else:
        all_listings = Listing.objects.filter(
                archived=False
            ).order_by('-last_bumped', sort)[start_index:entries]

    listings_count = Listing.objects.count()
    if listings_count % settings.ENTRIES_PER_PAGE == 0:
        total_pages = int(listings_count / settings.ENTRIES_PER_PAGE)
    else:
        total_pages = int(listings_count / settings.ENTRIES_PER_PAGE) + 1

    is_seller = request.user.has_perm('listings.add_listing')
    authenticated = request.user.is_authenticated
    if is_seller:
        seller = Seller.objects.get(connected_user=request.user)
    else:
        seller = request.user

    last_used_address = request.session.get('last_address')
    contact1 = request.session.get('contact1')
    contact2 = request.session.get('contact2')
    contact3 = request.session.get('contact3')
    contact4 = request.session.get('contact4')
    contact5 = request.session.get('contact5')
    saved_contacts_raw = [contact1, contact2, contact3, contact4, contact5]
    saved_contacts = list(filter((None).__ne__, saved_contacts_raw))

    return render(request, 'listings/index.htm', {
        'listings': all_listings,
        'is_seller': is_seller,
        'authenticated': authenticated,
        'seller': seller,
        'contacts': saved_contacts,
        'address': last_used_address,
        'pages': range(total_pages),
        'current_page': page,
        'sort': sort
    })

def listing(request, listing_id):
    list = get_object_or_404(Listing, pk=listing_id)
    if list.archived:
        return HttpResponseRedirect(reverse('index'))
    emails = list.contact.contact_emails
    if emails:
        emails = emails.split(',')
    view_count = ListingView.objects.filter(listing=list).count()

    if not list.address.lat:
        address_latlng = geocode(str(list.address))
        if address_latlng[0]:
            list.address.lat = address_latlng[0]
            list.address.lng = address_latlng[1]
            list.address.save()

    delta = timezone.now() - list.last_bumped

    page_data = {
        'id': list.id,
        'title': list.title,
        'seller': {
            'username': list.seller.username,
            'rating': list.seller.rating,
            'is_current_user': request.user == list.seller.connected_user
        },
        'type': list.type,
        'description': list.description,
        'price': list.price,
        'images': list.images.all(),
        'contact': {
            'name': list.contact.name,
            'social_contacts': ast.literal_eval(list.contact.social_contacts),
            'phone_numbers': ast.literal_eval(list.contact.phone_numbers),
            'call_time_start': list.contact.call_time.split('-')[0],
            'call_time_end': list.contact.call_time.split('-')[1],
            'contact_emails': emails
        },
        'address': {
            'string': str(list.address),
            'lat': list.address.lat,
            'lng': list.address.lng,
            'town': list.address.town,
            'district': list.address.district,
            'street_name': list.address.street_name,
            'house_number': list.address.house_number,
            'apartment': list.address.apartment,
            'postcode': list.address.postcode,
            'static': 'https://maps.googleapis.com/maps/api/staticmap?zoom=14&size=534x330&markers=' +
                str(list.address.lat) + ',' + str(list.address.lng) +
                '&key=AIzaSyDNYFzufFNdmzKAtT0sixE6l-FC_LqhrqQ&language=' +
                settings.LANGUAGE_CODE
        },
        'views': view_count,
        'can_bump': delta.days >= 1,
        'user_authenticated': request.user.is_authenticated
    }

    ip = get_client_ip(request)
    view = ListingView.objects.get_or_create(ip=ip, listing=list)

    if "App/" in request.META['HTTP_USER_AGENT']:
        return JsonResponse(page_data)
    else:
        return render(request, 'listings/listing.htm', {'listing': page_data})

def listing_delete(request, listing_id):
    list = get_object_or_404(Listing, pk=listing_id)
    same_user = request.user == list.seller.connected_user
    if not same_user:
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    if request.method == 'POST' and same_user:
        list.archived = True
        list.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, 'listings/delete.htm', {'listing': list})

def listing_bump(request, listing_id):
    list = get_object_or_404(Listing, pk=listing_id)
    same_user = request.user == list.seller.connected_user
    if same_user:
        delta = timezone.now() - list.last_bumped
        if delta.days >= 1:
            list.last_bumped = timezone.now()
            list.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return HttpResponse('You can bump your listing only once per day')
    else:
        return HttpResponseRedirect(reverse('listing', args=[listing_id]))

@permission_required('listings.add_listing', login_url='seller_add')
def listing_create(request, listing_id=0):
    if listing_id != 0:
        listing = get_object_or_404(Listing, pk=listing_id)
        same_user = listing.seller.connected_user == request.user
        if not same_user:
            return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    last_used_address = request.session.get('last_address')
    contact1 = request.session.get('contact1')
    contact2 = request.session.get('contact2')
    contact3 = request.session.get('contact3')
    contact4 = request.session.get('contact4')
    contact5 = request.session.get('contact5')
    saved_contacts_raw = [contact1, contact2, contact3, contact4, contact5]
    # Clear all None values
    saved_contacts = list(filter((None).__ne__, saved_contacts_raw))

    # If no contacts are saved in cookies, try to get
    # last five from the database
    if saved_contacts == []:
        try:
            saved_contacts_query = Contact.objects.filter(seller=Seller.objects
                .get(connected_user=request.user)).order_by('-id')[:5]
            i = 1
            for saved_contact in saved_contacts_query:
                cntct = {
                    'id': saved_contact.id,
                    'name': saved_contact.name,
                    'phone_numbers': saved_contact.phone_numbers,
                    'call_time': saved_contact.call_time,
                    'social_contacts': saved_contact.social_contacts,
                    'contact_emails': saved_contact.contact_emails
                }
                request.session['contact' + str(i)] = cntct
                saved_contacts.append(cntct)
                i += 1
        except ObjectDoesNotExist:
            # No saved contacts
            pass

    edit_contact = None
    if listing_id != 0:
        i = 1
        for c in saved_contacts:
            if c['id'] == listing.contact.id:
                edit_contact = i
                break
            i += 1

    if request.method == 'POST':
        if listing_id == 0:
            form = CreateListingForm(request.POST)
            address_form = AddressForm(request.POST)
        else:
            form = EditListingForm(request.POST, instance=listing)
            address_form = EditAddressForm(request.POST, instance=listing.address)
        contact_form = ContactForm(request.POST)

        if contact_form.is_valid() and address_form.is_valid() and form.is_valid():
            if not re.fullmatch(r'\w+ *\w* *\w*', contact_form.cleaned_data['contact_name']):
                contact_form.add_error('contact_name', _('Incorrect name format'))

            phone_nums = ['phone_number1', 'phone_number2', 'phone_number3',
                'phone_number4']
            for num in phone_nums:
                number = contact_form.cleaned_data[num]
                if number and not re.fullmatch(r'\+*\d+', number):
                    contact_form.add_error(num, _('Check if the number is correct'))

            ct_start = contact_form.cleaned_data['call_time_start']
            ct_end = contact_form.cleaned_data['call_time_end']
            if ct_start and ct_end:
                ct_start = ct_start.strftime('%H:%M')
                ct_end = ct_end.strftime('%H:%M')
                if ct_start < ct_end:
                    call_time = ct_start + '-' + ct_end
                else:
                    contact_form.add_error('ct_start', _('Time period is invalid'))
            elif ct_start:
                call_time = ct_start.strftime('%H:%M') + '-23:59'
            elif ct_end:
                call_time = '0:00-' + ct_end.strftime('%H:%M')
            else:
                call_time = '0:00-23:59'

            phone_nums_formatted = make_dict([
                contact_form.cleaned_data['phone_operator1'],
                contact_form.cleaned_data['phone_operator2'],
                contact_form.cleaned_data['phone_operator3'],
                contact_form.cleaned_data['phone_operator4']
            ], [
                contact_form.cleaned_data['phone_number1'],
                contact_form.cleaned_data['phone_number2'],
                contact_form.cleaned_data['phone_number3'],
                contact_form.cleaned_data['phone_number4']
            ], False)

            social_contacts_formatted = make_dict([
                contact_form.cleaned_data['social_network1'],
                contact_form.cleaned_data['social_network2'],
                contact_form.cleaned_data['social_network3'],
                contact_form.cleaned_data['social_network4']
            ], [
                contact_form.cleaned_data['social_contact1'],
                contact_form.cleaned_data['social_contact2'],
                contact_form.cleaned_data['social_contact3'],
                contact_form.cleaned_data['social_contact4']
            ], True)

            emails_formatted = contact_form.cleaned_data['contact_email1']
            if contact_form.cleaned_data['contact_email2']:
                emails_formatted += ',' + contact_form.cleaned_data['contact_email2']

            new_address = Address(
                town = address_form.cleaned_data['town'],
                district = address_form.cleaned_data['district'],
                street_name = address_form.cleaned_data['street_name'],
                house_number = address_form.cleaned_data['house_number'],
                apartment = address_form.cleaned_data['apartment'],
                postcode = address_form.cleaned_data['postcode']
            )

            if listing_id == 0:
                current_seller = Seller.objects.get(connected_user=request.user)
                today_listings = Listing.objects.filter(seller=current_seller,
                    date_added__date=timezone.now().date())
                if len(today_listings) >= 3:
                    form.add_error(None, _('You have reached your daily limit'))
                title = form.cleaned_data['title']
                if len(title) < 5:
                    form.add_error('title', _('The title is too short'))
                elif re.match(r'[^a-zA-Z0-9 а-яА-Я\'"]', title):
                    form.add_error('title',
                        _('The title contains illegal characters'))
                right_type = form.cleaned_data[
                    'type'
                ] == 'SELL' or form.cleaned_data['type'] == 'BUY'
                if not right_type:
                    form.add_error('type', _('Invalid type'))

            if form.cleaned_data['price'] < 0 or form.cleaned_data[
                'price'] > settings.MAX_PRICE:
                form.add_error('price', _('The price is out of range'))
            if len(
                form.cleaned_data['description']
            ) < settings.MIN_DESCRIPTION_LENGTH:
                form.add_error('description', _('The description is too short'))

            contact_select = request.POST.get('contact')
            # If user has less than 5 saved contacts, than save it
            if contact_select == 'new':
                i = 1
                for contact_raw in saved_contacts_raw:
                    if contact_raw == None:
                        new_contact = Contact(
                            seller = Seller.objects.get(pk=request.user),
                            name = contact_form.cleaned_data['contact_name'],
                            phone_numbers = phone_nums_formatted,
                            social_contacts = social_contacts_formatted,
                            contact_emails = emails_formatted
                        )
                        new_contact.save()

                        request.session['contact' + str(i)] = {
                            'id': new_contact.id,
                            'name': contact_form.cleaned_data['contact_name'],
                            'phone_numbers': phone_nums_formatted,
                            'call_time': call_time,
                            'social_contacts': social_contacts_formatted,
                            'contact_emails': emails_formatted
                        }
                        break
                    i += 1
            elif 'contact' in contact_select:
                new_contact = Contact.objects.get(pk=request.session[contact_select]['id'])
                new_contact.seller = Seller.objects.get(pk=request.user)
                new_contact.name = contact_form.cleaned_data['contact_name']
                new_contact.phone_numbers = phone_nums_formatted
                new_contact.call_time = call_time
                new_contact.social_contacts = social_contacts_formatted
                new_contact.contact_emails = emails_formatted
                new_contact.save()

                request.session[contact_select] = {
                    'id': new_contact.id,
                    'name': contact_form.cleaned_data['contact_name'],
                    'phone_numbers': phone_nums_formatted,
                    'call_time': call_time,
                    'social_contacts': social_contacts_formatted,
                    'contact_emails': emails_formatted
                }

            request.session['last_address'] = {
                'town': address_form.cleaned_data['town'],
                'district': address_form.cleaned_data['district'],
                'street_name': address_form.cleaned_data['street_name'],
                'house_number': address_form.cleaned_data['house_number'],
                'apartment': address_form.cleaned_data['apartment'],
                'postcode': address_form.cleaned_data['postcode']
            }

            if len(form.errors) == 0:
                address_hash = hash_address(new_address)
                try:
                    new_address = Address.objects.get(hash=address_hash)
                except ObjectDoesNotExist:
                    address_latlng = geocode(str(new_address))
                    if address_latlng[0]:
                        new_address.lat = address_latlng[0]
                        new_address.lng = address_latlng[1]
                    new_address.save()

                images = request.FILES.getlist('images')
                uploaded_images = []
                if images:
                    # Maximum 10 images
                    if len(images) > 10:
                        images = images[:9]
                    for image in images:
                        uploaded_image = UploadedImage(
                            user=request.user,
                            file=image,
                            thumbnail=image
                        )
                        uploaded_image.save()
                        resize_image(uploaded_image.file.path, 960)
                        resize_image(uploaded_image.thumbnail.path, 180, scale=True)
                        uploaded_images.append(uploaded_image)

                # listing_id is zero when creating listing, when editing it
                # equals to the id of the listing user is editing
                if listing_id != 0:
                    if same_user:
                        listing.price = form.cleaned_data['price']
                        listing.description = form.cleaned_data['description']
                        listing.address = new_address
                        listing.contact = new_contact
                        listing.last_modified = timezone.now()
                        listing.save()
                        listing.images.set(uploaded_images)
                    else:
                        return HttpResponse('You cannot edit another user\'s listings')
                else:
                    new_listing = Listing(
                        title = form.cleaned_data['title'],
                        seller = current_seller,
                        type = form.cleaned_data['type'],
                        price = form.cleaned_data['price'],
                        description = form.cleaned_data['description'],
                        address = new_address,
                        contact = new_contact
                    )
                    new_listing.save()
                    new_listing.images.set(uploaded_images)
                return HttpResponseRedirect(reverse('listing', args=[
                    new_listing.id
                ]))
        else:
            form.add_error(None, _('Check if the form is correct'))
    else:
        contact_form = ContactForm()
        if listing_id == 0:
            address_form = AddressForm(last_used_address)
            form = CreateListingForm()
        else:
            address_form = EditAddressForm(instance=listing.address)
            form = EditListingForm(instance=listing)

    return render(request, 'listings/create.htm', {
        'form': form,
        'contact_form': contact_form,
        'address_form': address_form,
        'last_address': last_used_address,
        'saved_contacts': saved_contacts,
        'edit_contact': edit_contact
    })

def seller(request, seller_username):
    seller = get_object_or_404(Seller, username=seller_username)
    seller_listings = Listing.objects.filter(seller=seller)
    seller_reviews = Review.objects.filter(target_seller=seller)
    self_view = request.user == seller.connected_user
    try:
        review = seller_reviews.get(username=request.user.get_username())
        star_rating(review)
    except ObjectDoesNotExist:
        # User hasn't reviewed this seller
        review = None

    if request.method == 'POST':
        if self_view or review:
            return HttpResponse(_('Review cannot be added'))

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            rating = review_form.cleaned_data['rating']
            if rating < 1 or rating > 5:
                return HttpResponse('Rating must be in between 1 and 5')
            elif len(review_form.cleaned_data['text']) < 5:
                return HttpResponse('The text is too short')

            target_seller = Seller.objects.get(username=seller_username)
            all_reviews = Review.objects.filter(target_seller=target_seller)

            new_review = Review(
                target_seller = target_seller,
                username = request.user.get_username(),
                rating = review_form.cleaned_data['rating'],
                text = review_form.cleaned_data['review_text']
            )
            new_review.save()

            # If seller has more than 3 reviews, update his rating based on
            # the average review rating
            if len(all_reviews) > 3:
                total_rating = 0
                for review in all_reviews:
                    total_rating += review.rating
                avg_rating = total_rating / len(all_reviews)

                print(avg_rating)

                target_seller.rating = int(round(avg_rating))
                target_seller.save()

            return HttpResponseRedirect(reverse('seller_profile',
                args=[target_seller.username]))
    else:
        review_form = ReviewForm()

    # Converting numeric rating to symbols (stars)
    for seller_review in seller_reviews:
        star_rating(seller_review)

    return render(request, 'listings/seller.htm', {
        'seller': seller,
        'listings': seller_listings,
        'reviews': seller_reviews,
        'review_form': review_form,
        'self': self_view,
        'review': review,
        'authenticated': request.user.is_authenticated
    })

@login_required
def seller_add(request):
    if Seller.objects.filter(connected_user=request.user).exists():
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'POST':
        seller_form = SellerForm(request.POST, request.FILES)
        if seller_form.is_valid():
            seller_username = seller_form.cleaned_data['seller_username']
            if seller_username in settings.RESERVED_KEYWORDS:
                seller_form.add_error('seller_username',
                    _('You can\'t use this username'))
            elif Seller.objects.filter(username=seller_username).exists():
                seller_form.add_error('seller_username',
                    _('User with this username already exists'))
            elif len(seller_username) < 4:
                seller_form.add_error('seller_username',
                    _('Username must be at least 4 characters long'))
            elif not re.match(r'[a-zA-Z]+?[a-zA-Z0-9_]+[a-zA-Z0-9]$',
                seller_username):
                seller_form.add_error('seller_username',
                    _('Username can contain only latin caharacters. '
                     'It must start with a letter and end with a'
                     ' letter or a digit'))

            phone = seller_form.cleaned_data['mobile_phone']
            if len(phone) < 6 or len(phone) > 16:
                seller_form.add_error('mobile_phone',
                    _('Number is of invalid length'))
            elif not re.fullmatch(r'\+{0,1}\d+', phone, flags=re.ASCII):
                seller_form.add_error('mobile_phone',
                    _('Number can contain only plus sign and digits'))

            names = seller_form.cleaned_data['full_name'].split(' ')
            if len(names) < settings.FULL_NAME_PARTS:
                seller_form.add_error('full_name',
                    _('Please, specify the full name'))
            else:
                for name in names:
                    if len(name) < 2:
                        seller_form.add_error('full_name',
                            _('Check if the name is correct'))
                        break

            if len(seller_form.errors) == 0:
                request.user.groups.add(1)
                new_seller = Seller(
                    connected_user = request.user,
                    full_name = seller_form.cleaned_data['full_name'],
                    avatar = seller_form.cleaned_data['avatar'],
                    show_name = seller_form.cleaned_data['show_name'],
                    username = seller_username.lower(),
                    mobile_phone = phone
                )
                new_seller.save()
                if new_seller.avatar:
                    resize_image(new_seller.avatar.path, 1, scale=True)
                return HttpResponseRedirect(reverse('index'))
    else:
        seller_form = SellerForm()
    return render(request, 'listings/newseller.htm', {'seller_form': seller_form})

@login_required
def review_edit(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    if review.username != request.user.get_username():
        return HttpResponseRedirect(reverse('seller_profile', args=[
            review.target_seller.username
        ]))

    if request.method == 'POST':
        edit_text = request.POST.get('add_text').strip()
        try:
            rating = int(request.POST.get('rating'))
        except ValueError:
            return HttpResponse('Rating must be a number')
        if rating < 1 or rating > 5:
            return HttpResponse('Rating must be in between 1 and 5')
        elif len(edit_text) < 5:
            return HttpResponse('The text is too short')
        elif review.date_edited:
            return HttpResponse('You have already edited this review')
        else:
            review.rating = rating
            review.additional_text = edit_text
            review.date_edited = timezone.now()
            review.save()
            return HttpResponseRedirect(reverse('seller_profile', args=[
                review.target_seller.username
            ]))
    return render(request, 'listings/review.htm', {'review': review})
