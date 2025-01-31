# Generated by Django 5.1.5 on 2025-01-27 15:53

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0001_initial"),
        ("borrowings", "0002_rename_book_id_borrowing_book_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="borrowing",
            options={},
        ),
        migrations.AddField(
            model_name="borrowing",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="book",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to="books.book",
            ),
        ),
        migrations.AlterField(
            model_name="borrowing",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="borrowings",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="borrowing",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ("expected_return_date__gt", models.F("borrow_date"))
                ),
                name="check_expected_after_borrow",
            ),
        ),
    ]
