# Generated by Django 2.1.3 on 2018-11-18 17:35

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import listings.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('cached_id', models.CharField(editable=False, max_length=32, unique=True)),
                ('town', models.CharField(max_length=40)),
                ('district', models.CharField(blank=True, max_length=30, null=True)),
                ('street_name', models.CharField(blank=True, max_length=50, null=True)),
                ('house_number', models.CharField(blank=True, max_length=7, null=True)),
                ('apartment', models.PositiveIntegerField(blank=True, null=True)),
                ('postcode', models.CharField(blank=True, max_length=8, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone_numbers', models.CharField(max_length=150, validators=[django.core.validators.RegexValidator(code='phone_format_incorrect', message='Incorrect format', regex='{("\\w+":"\\+*\\d+",){,3}("\\w+":"\\+*\\d+"){1}}')])),
                ('social_contacts', models.CharField(default='{}', max_length=282, validators=[django.core.validators.RegexValidator(code='social_format_incorrect', message='Incorrect format', regex='{("\\w+":"\\S+?",){,3}("\\w+":"\\S+?"){,1}}')])),
                ('contact_emails', models.CharField(blank=True, max_length=70, null=True, validators=[django.core.validators.RegexValidator(code='emails_format_incorrect', message='Incorrect format', regex='(\\w+?@\\w+?\\.\\w{2,3},){,2}')])),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=140)),
                ('image', models.ImageField(upload_to='files/userimages/listings')),
                ('type', models.CharField(choices=[('SELL', 'Selling'), ('BUY', 'Buying')], default='SELL', max_length=4)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[listings.models.unsigned])),
                ('description', models.TextField()),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('total_views', models.IntegerField(default=0)),
                ('users_views', models.IntegerField(default=0)),
                ('archived', models.BooleanField(default=False)),
                ('sold', models.BooleanField(default=False)),
                ('last_bumped', models.DateTimeField(default=datetime.datetime(1970, 12, 1, 12, 0))),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='listings.Address')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='listings.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=30)),
                ('rating', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('text', models.TextField(blank=True, null=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('additional_text', models.CharField(blank=True, max_length=150, null=True)),
                ('edit_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('connected_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('full_name', models.CharField(max_length=100, validators=[listings.models.validate_name])),
                ('show_name', models.BooleanField(default=False)),
                ('username', models.CharField(max_length=30, unique=True)),
                ('rating', models.PositiveIntegerField(default=3, editable=False)),
                ('mobile_phone', models.CharField(max_length=20, validators=[django.core.validators.RegexValidator(code='number_format_incorrect', message='Incorrect number format', regex='\\+\\d{9,18}')])),
                ('join_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='review',
            name='target_seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listings.Seller'),
        ),
        migrations.AddField(
            model_name='listing',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listings.Seller'),
        ),
        migrations.AddField(
            model_name='contact',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='listings.Seller'),
        ),
    ]
