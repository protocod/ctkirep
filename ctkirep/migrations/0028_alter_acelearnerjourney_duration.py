# Generated by Django 4.0.4 on 2022-05-09 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctkirep', '0027_acelearnerjourney_attempt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='acelearnerjourney',
            name='duration',
            field=models.DurationField(null=True, verbose_name='Reading duration'),
        ),
    ]
