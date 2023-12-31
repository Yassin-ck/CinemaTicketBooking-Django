# Generated by Django 4.2.6 on 2023-12-11 09:35

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Languages",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="MoviesDetails",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("movie_name", models.CharField(max_length=200)),
                ("director", models.CharField(max_length=100)),
                (
                    "poster",
                    models.ImageField(
                        blank=True, null=True, upload_to="movie_posters/"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("UPCOMING", "UPCOMING"),
                            ("CURRENTLYPLAYING", "CURRENTLY PLAYING"),
                            ("RELEASED", "RELEASED"),
                        ],
                        default="UPCOMING",
                        max_length=20,
                    ),
                ),
            ],
            options={
                "ordering": ("id",),
                "unique_together": {("movie_name", "director")},
            },
        ),
    ]
