# Generated by Django 3.2.5 on 2021-07-16 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banco', '0002_auto_20210715_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccion',
            name='monto',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
