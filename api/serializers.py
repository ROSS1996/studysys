# serializers.py
from rest_framework import serializers
from .models import (
    Banca, Concurso, Disciplina, Topico, ConcursoTopico, Questao, QuestaoTopico
)

class BancaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banca
        fields = '__all__'

class ConcursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concurso
        fields = '__all__'

class DisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = '__all__'

class TopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topico
        fields = '__all__'

class ConcursoTopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcursoTopico
        fields = '__all__'

class QuestaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = '__all__'

class QuestaoTopicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestaoTopico
        fields = '__all__'