# Generated by Django 4.2.5 on 2024-02-28 06:26

from django.db import migrations, models
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0003_alter_product_tags"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productimage",
            options={
                "verbose_name": "Изображение",
                "verbose_name_plural": "Изображения",
            },
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(
                default="products/default.jpg",
                upload_to=shopapp.models.product_images_directory_path,
            ),
        ),
    ]
