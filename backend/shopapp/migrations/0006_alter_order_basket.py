# Generated by Django 4.2.5 on 2024-02-28 13:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shopapp", "0005_alter_sale_options_remove_product_count_of_orders_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="basket",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order",
                to="shopapp.basket",
            ),
        ),
    ]