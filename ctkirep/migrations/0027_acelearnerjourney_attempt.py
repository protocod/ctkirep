# Generated by Django 4.0.4 on 2022-05-08 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ctkirep', '0026_aceaction_alter_acestatus_id_acelearnerjourney'),
    ]

    operations = [
        migrations.AddField(
            model_name='acelearnerjourney',
            name='attempt',
            field=models.SmallIntegerField(default=1, verbose_name='Attempt'),
            preserve_default=False,
        ),
    ]
