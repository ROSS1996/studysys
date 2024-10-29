# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BancaViewSet, ConcursoViewSet, DisciplinaViewSet,
    TopicoViewSet, ConcursoTopicoViewSet,
    QuestaoViewSet, QuestaoTopicoViewSet
)

router = DefaultRouter()
router.register(r'bancas', BancaViewSet)
router.register(r'concursos', ConcursoViewSet)
router.register(r'disciplinas', DisciplinaViewSet)
router.register(r'topicos', TopicoViewSet)
router.register(r'concurso-topicos', ConcursoTopicoViewSet)
router.register(r'questoes', QuestaoViewSet)
router.register(r'questao-topicos', QuestaoTopicoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]