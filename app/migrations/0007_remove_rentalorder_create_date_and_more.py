# Generated by Django 4.2 on 2023-07-02 02:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_rentalorder_create_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rentalorder',
            name='create_date',
        ),
        migrations.AddField(
            model_name='rentalorder',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
