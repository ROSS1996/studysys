# views.py
from rest_framework import viewsets
from .models import (
    Banca, Concurso, Disciplina, Topico, ConcursoTopico, Questao, QuestaoTopico
)
from .serializers import (
    BancaSerializer, ConcursoSerializer, DisciplinaSerializer,
    TopicoSerializer, ConcursoTopicoSerializer,
    QuestaoSerializer, QuestaoTopicoSerializer
)

class BancaViewSet(viewsets.ModelViewSet):
    queryset = Banca.objects.all()
    serializer_class = BancaSerializer

class ConcursoViewSet(viewsets.ModelViewSet):
    queryset = Concurso.objects.all()
    serializer_class = ConcursoSerializer

class DisciplinaViewSet(viewsets.ModelViewSet):
    queryset = Disciplina.objects.all()
    serializer_class = DisciplinaSerializer

class TopicoViewSet(viewsets.ModelViewSet):
    queryset = Topico.objects.all()
    serializer_class = TopicoSerializer

class ConcursoTopicoViewSet(viewsets.ModelViewSet):
    queryset = ConcursoTopico.objects.all()
    serializer_class = ConcursoTopicoSerializer


class QuestaoViewSet(viewsets.ModelViewSet):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer

class QuestaoTopicoViewSet(viewsets.ModelViewSet):
    queryset = QuestaoTopico.objects.all()
    serializer_class = QuestaoTopicoSerializer