# Generated by Django 4.2.7 on 2023-12-28 23:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tasks",
            old_name="link",
            new_name="uri",
        ),
        migrations.AddField(
            model_name="tasks",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="tasks",
            name="queue_jumps",
            field=models.PositiveBigIntegerField(default=10),
        ),
        migrations.AddField(
            model_name="tasks",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="tasks",
            name="description",
            field=models.TextField(max_length=255),
        ),
        migrations.AlterField(
            model_name="tasks",
            name="display_order",
            field=models.PositiveIntegerField(unique=True),
        ),
    ]