# Generated by Django 4.2.6 on 2023-11-01 06:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("theatre_dashboard", "0013_remove_theatredetails_is_loginned"),
    ]

    operations = [
        migrations.AlterField(
            model_name="theareownerdetails",
            name="id_proof",
            field=models.ImageField(upload_to="owner_id_proof/"),
        ),
    ]
