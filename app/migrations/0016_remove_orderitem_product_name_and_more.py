# Generated by Django 4.2 on 2024-11-25 03:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_orderitem_product_alter_orderitem_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='product_price',
        ),
    ]
