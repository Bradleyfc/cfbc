# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_registro_carnet_registro_correo_registro_grado_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registro',
            name='ocupacion',
            field=models.CharField(
                choices=[
                    ('ocupacion1', 'Desocupado'),
                    ('ocupacion2', 'Estudiante'),
                    ('ocupacion3', 'Ama de Casa'),
                    ('ocupacion4', 'Trabajador Estatal'),
                    ('ocupacion5', 'Trabajador por Cuenta Propia')
                ],
                default='ocupacion1',
                max_length=100
            ),
        ),
    ]