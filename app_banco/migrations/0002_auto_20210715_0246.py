# Generated by Django 3.2.5 on 2021-07-15 02:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_banco', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaccion',
            options={'verbose_name_plural': 'Transacciones'},
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='destino',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='destino', to='app_banco.cuenta'),
        ),
        migrations.AlterField(
            model_name='transaccion',
            name='origen',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origen', to='app_banco.cuenta'),
        ),
    ]
