# Generated by Django 4.2.6 on 2023-10-26 04:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentications', '0001_initial'),
        ('theatre_dashboard', '0006_alter_theatredetails_certification'),
    ]

    operations = [
        migrations.AddField(
            model_name='theareownerdetails',
            name='address',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='theareownerdetails',
            name='alternative_contact',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='theatredetails',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentications.location'),
        ),
    ]