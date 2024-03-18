# Generated by Django 4.2.5 on 2024-02-28 12:55

from django.db import migrations, models
import myauth.models


class Migration(migrations.Migration):

    dependencies = [
        ("myauth", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profileuser",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="profile/avatar_default.png",
                null=True,
                upload_to=myauth.models.avatar_image_directory_path,
            ),
        ),
    ]
