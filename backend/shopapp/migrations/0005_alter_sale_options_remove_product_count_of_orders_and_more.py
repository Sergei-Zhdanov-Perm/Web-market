# Generated by Django 4.2.5 on 2024-02-28 12:55

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ("myauth", "0002_alter_profileuser_avatar"),
        ("shopapp", "0004_alter_productimage_options_alter_productimage_image"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sale",
            options={"verbose_name": "Скидка", "verbose_name_plural": "Скидки"},
        ),
        migrations.RemoveField(
            model_name="product",
            name="count_of_orders",
        ),
        migrations.AlterField(
            model_name="basketitem",
            name="basket",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="items",
                to="shopapp.basket",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True,
                default="categories/default.jpg",
                null=True,
                upload_to=shopapp.models.category_image_directory_path,
                verbose_name="Изображение",
            ),
        ),
        migrations.AlterField(
            model_name="category",
            name="title",
            field=models.CharField(max_length=200, verbose_name="Название категории"),
        ),
        migrations.AlterField(
            model_name="order",
            name="basket",
            field=models.OneToOneField(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order",
                to="shopapp.basket",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="delivery_type",
            field=models.CharField(
                choices=[("delivery", "Доставка"), ("express", "Экспресс доставка")],
                default="Доставка",
                max_length=20,
                verbose_name="Тип доставки",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="payment_type",
            field=models.CharField(
                choices=[
                    ("online", "Онлайн оплата"),
                    ("online_any", "Онлайн оплата со случайного счета"),
                ],
                default="Онлайн оплата",
                max_length=20,
                verbose_name="Способ оплаты",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="products",
            field=models.ManyToManyField(
                related_name="orders", to="shopapp.product", verbose_name="Продукты"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                default="inProgress", max_length=255, verbose_name="Статус заказа"
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="myauth.profileuser",
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="rate",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (5, "Очень хорошо"),
                    (4, "Хорошо"),
                    (3, "Нормально"),
                    (2, "Плохо"),
                    (1, "Очень плохо"),
                ],
                validators=[django.core.validators.MaxValueValidator(5)],
                verbose_name="Оценка",
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="text",
            field=models.TextField(blank=True, null=True, verbose_name="Текст отзыва"),
        ),
        migrations.AlterField(
            model_name="sale",
            name="date_from",
            field=models.DateField(verbose_name="Дата начала скидки"),
        ),
        migrations.AlterField(
            model_name="sale",
            name="date_to",
            field=models.DateField(verbose_name="Дата окончания скидки"),
        ),
        migrations.AlterField(
            model_name="sale",
            name="discount",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="Скидка"
            ),
        ),
        migrations.AlterField(
            model_name="sale",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sale_info",
                to="shopapp.product",
                verbose_name="Продукт",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Название тега"),
        ),
    ]