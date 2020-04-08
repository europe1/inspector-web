# Generated by Django 2.1.3 on 2018-11-24 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_auto_20181124_1423'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='question',
            name='selected_answer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='questions.Answer'),
        ),
    ]