# Generated by Django 4.2.6 on 2023-11-18 01:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("theatre_dashboard", "0016_showdates_remove_shows_end_date_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="shows",
            old_name="dates",
            new_name="show_dates",
        ),
    ]