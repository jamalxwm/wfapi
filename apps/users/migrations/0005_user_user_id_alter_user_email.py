# Generated by Django 4.2.7 on 2023-11-29 18:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_remove_user_active_tier_remove_user_floater"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="user_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="email address"
            ),
        ),
    ]
