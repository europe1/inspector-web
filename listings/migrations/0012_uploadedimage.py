# Generated by Django 2.1.3 on 2018-11-26 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0011_auto_20181126_0856'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=80, null=True)),
                ('file', models.ImageField(upload_to='files/userimages')),
            ],
        ),
    ]
