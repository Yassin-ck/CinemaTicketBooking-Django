# Generated by Django 4.2.6 on 2023-11-14 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("admin_dashboard", "0001_initial"),
        (
            "theatre_dashboard",
            "0006_rename_seating_screenseatarrangement_seating_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="screendetails",
            name="movies",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="admin_dashboard.moviesdetails",
            ),
        ),
    ]