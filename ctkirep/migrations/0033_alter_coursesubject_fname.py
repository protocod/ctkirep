# Generated by Django 4.0.4 on 2022-06-10 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctkirep', '0032_alter_acecontentstatus_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesubject',
            name='fname',
            field=models.CharField(max_length=100, verbose_name='Subject name'),
        ),
    ]
