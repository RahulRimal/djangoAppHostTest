# Generated by Django 4.1.1 on 2022-09-19 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_customer_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.ImageField(null=True, upload_to='customer/images'),
        ),
    ]