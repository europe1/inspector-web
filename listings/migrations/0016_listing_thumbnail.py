# Generated by Django 2.1.3 on 2018-11-27 13:11

from django.db import migrations, models
import listings.models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0015_auto_20181127_1604'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='thumbnail',
            field=models.ImageField(default='thumbnail.jpg', upload_to='userimages/listings/271118'),
        ),
    ]