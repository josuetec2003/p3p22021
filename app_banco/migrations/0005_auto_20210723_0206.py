# Generated by Django 3.2.5 on 2021-07-23 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_banco', '0004_cliente_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaccion',
            name='comentario',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='movimiento',
            field=models.CharField(choices=[('1', 'Deposito'), ('2', 'Retiro'), ('3', 'Transferencia')], max_length=1),
        ),
    ]
