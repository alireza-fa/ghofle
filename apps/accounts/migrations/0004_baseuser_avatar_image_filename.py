# Generated by Django 5.0.3 on 2024-07-27 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='avatar_image_filename',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True),
        ),
    ]
