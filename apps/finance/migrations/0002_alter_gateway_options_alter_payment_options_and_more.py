# Generated by Django 5.0.3 on 2024-03-31 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gateway',
            options={'verbose_name': 'Gateway', 'verbose_name_plural': 'Gateways'},
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={'verbose_name': 'Payment', 'verbose_name_plural': 'Payments'},
        ),
        migrations.AddField(
            model_name='gateway',
            name='callback_url',
            field=models.CharField(default='http://localhost/finance/verify/', max_length=120, verbose_name='callback url'),
            preserve_default=False,
        ),
    ]