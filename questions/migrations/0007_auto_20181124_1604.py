# Generated by Django 2.1.3 on 2018-11-24 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0006_auto_20181124_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='tags',
            field=models.CharField(default='general', max_length=100),
        ),
    ]
