# Generated by Django 5.0.7 on 2024-11-09 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_remove_questao_acerto_remove_questao_correta_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questao',
            name='alternativa_1',
            field=models.TextField(default='Verdadeiro'),
        ),
        migrations.AlterField(
            model_name='questao',
            name='alternativa_2',
            field=models.TextField(default='Falso'),
        ),
        migrations.AlterField(
            model_name='questao',
            name='correta',
            field=models.IntegerField(default=1),
        ),
    ]
