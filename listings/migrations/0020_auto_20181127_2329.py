# Generated by Django 2.1.3 on 2018-11-27 20:29

from django.db import migrations, models
import listings.models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0019_auto_20181127_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='thumbnail',
            field=models.ImageField(default='thumbnail.jpg', upload_to=listings.models.Listing.upload_path),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='file',
            field=models.ImageField(upload_to='userimages/listings/%d%m%y'),
        ),
        migrations.AlterField(
            model_name='uploadedimage',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to='userimages/listings/%d%m%y/thumbnails'),
        ),
    ]
