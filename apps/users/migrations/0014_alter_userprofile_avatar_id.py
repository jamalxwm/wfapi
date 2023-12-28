# Generated by Django 4.2.7 on 2023-12-28 18:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("floaters", "0007_rename_floaters_floater"),
        ("users", "0013_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="avatar_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="floaters.floater",
                verbose_name="Floater ID",
            ),
        ),
    ]
