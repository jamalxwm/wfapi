# Generated by Django 4.2.7 on 2023-11-28 21:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("floaters", "0006_floaters_avatar_badge_1x_floaters_avatar_badge_2x_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Floaters",
            new_name="Floater",
        ),
    ]
