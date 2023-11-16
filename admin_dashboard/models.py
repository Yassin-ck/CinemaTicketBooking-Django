from django.contrib.gis.db import models


class Languages(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


class MoviesDetails(models.Model):
    STATUS = [
        ("UPCOMING", "UPCOMING"),
        ("CURRENTLYPLAYING", "CURRENTLY PLAYING"),
        ("RELEASED", "RELAESED"),
    ]
    movie_name = models.CharField(max_length=200)
    languages = models.ManyToManyField(Languages, related_name="movie_language")
    director = models.CharField(max_length=100)
    poster = models.ImageField(upload_to="movie_posters/", null=True, blank=True)
    status = models.CharField(default="UPCOMING", choices=STATUS, max_length=20)

    class Meta:
        ordering = ("id",)
        unique_together = ("movie_name", "director")

    def __str__(self) -> str:
        return self.movie_name
