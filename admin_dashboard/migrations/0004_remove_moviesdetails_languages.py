# Generated by Django 4.2.6 on 2023-11-17 06:08

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "admin_dashboard",
            "0003_alter_moviesdetails_options_moviesdetails_director_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="moviesdetails",
            name="languages",
        ),
    ]