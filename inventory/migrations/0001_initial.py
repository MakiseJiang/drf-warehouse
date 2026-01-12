from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('material_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('model_number', models.CharField(max_length=200)),
                ('category', models.CharField(max_length=100)),
                ('equipment', models.CharField(max_length=200)),
                ('warehouse', models.CharField(max_length=100)),
                ('shelf', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
            ],
        ),
    ]