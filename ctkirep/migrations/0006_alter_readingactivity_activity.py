# Generated by Django 4.0.4 on 2022-04-28 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctkirep', '0005_readingactivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingactivity',
            name='activity',
            field=models.CharField(max_length=50, unique=True, verbose_name='Reading activity'),
        ),
    ]
