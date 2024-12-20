# Generated by Django 4.2 on 2024-11-25 04:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_remove_orderitem_product_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='municipality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.municipality'),
        ),
        migrations.AlterField(
            model_name='order',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.region'),
        ),
    ]
