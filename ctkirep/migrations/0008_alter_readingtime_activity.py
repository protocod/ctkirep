# Generated by Django 4.0.4 on 2022-04-29 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ctkirep', '0007_course_ractivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='readingtime',
            name='activity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ctkirep.readingactivity'),
        ),
    ]
