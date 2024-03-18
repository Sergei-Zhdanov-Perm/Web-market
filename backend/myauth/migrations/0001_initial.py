from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import myauth.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProfileUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200, verbose_name="Имя")),
                ("surname", models.CharField(max_length=200, verbose_name="Фамилия")),
                (
                    "patronymic",
                    models.CharField(max_length=200, verbose_name="Отчество"),
                ),
                (
                    "phone",
                    models.CharField(max_length=15, verbose_name="Номер телефона"),
                ),
                ("email", models.CharField(max_length=200, verbose_name="Email")),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=myauth.models.avatar_image_directory_path,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
