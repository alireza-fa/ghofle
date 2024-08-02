# Generated by Django 5.0.3 on 2024-07-27 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'image'), (2, 'Movie'), (3, 'pdf')], default=1, verbose_name='file type'),
            preserve_default=False,
        ),
    ]