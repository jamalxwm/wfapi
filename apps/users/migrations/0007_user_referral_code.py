# Generated by Django 4.2.7 on 2023-11-29 18:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_remove_user_user_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="referral_code",
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]