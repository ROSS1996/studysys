# Generated by Django 5.0.7 on 2024-10-29 19:44

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_questao_anulada_alter_questao_correta_3_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GrupoTopico',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='topico',
            name='grupo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.grupotopico'),
        ),
    ]
