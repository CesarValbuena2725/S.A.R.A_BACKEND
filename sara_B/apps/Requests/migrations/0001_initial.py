# Generated by Django 4.2 on 2025-03-29 21:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Access', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_plan', models.CharField(max_length=50, unique=True)),
                ('estado', models.CharField(choices=[('AC', 'Activo'), ('IN', 'Inactivo')], default='AC', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='TipoVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_vehiculo', models.CharField(max_length=50)),
                ('estado', models.CharField(choices=[('AC', 'Activo'), ('IN', 'Inactivo')], default='AC', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='VehiculoPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Requests.plan')),
                ('id_vehiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Requests.tipovehiculo')),
            ],
        ),
        migrations.CreateModel(
            name='Solicitud',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placa', models.CharField(max_length=6)),
                ('central_servicios', models.CharField(default='AutoSef', max_length=50)),
                ('estado', models.CharField(choices=[('AC', 'Activo'), ('CAL', 'Cancelado'), ('PRO', 'En Progreso')], default='AC', max_length=3)),
                ('turno', models.IntegerField()),
                ('telefono', models.CharField(max_length=10)),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
                ('observaciones', models.TextField(null=True)),
                ('id_empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Access.empleado')),
                ('id_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Requests.plan')),
                ('id_tipo_vehiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Requests.tipovehiculo')),
            ],
        ),
        migrations.AddConstraint(
            model_name='vehiculoplan',
            constraint=models.UniqueConstraint(fields=('id_plan', 'id_vehiculo'), name='Vehiculo_plan_pk'),
        ),
    ]
