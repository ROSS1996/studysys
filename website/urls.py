# urls.py
from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),  # Index view at the root URL

    path('bancas/', views.BancaListView.as_view(), name='banca_list'),
    path('bancas/new/', views.BancaCreateView.as_view(), name='banca_create'),
    path('bancas/<uuid:pk>/', views.BancaDetailView.as_view(), name='banca_detail'),
    path('bancas/<uuid:pk>/edit/', views.BancaUpdateView.as_view(), name='banca_edit'),

    path('concursos/', views.ConcursoListView.as_view(), name='concurso_list'),
    path('concursos/new/', views.ConcursoCreateView.as_view(), name='concurso_create'),
    path('concursos/<uuid:pk>/', views.ConcursoDetailView.as_view(), name='concurso_detail'),
    path('concursos/<uuid:pk>/edit/', views.ConcursoUpdateView.as_view(), name='concurso_edit'),

    path('disciplinas/', views.DisciplinaListView.as_view(), name='disciplina_list'),
    path('disciplinas/new/', views.DisciplinaCreateView.as_view(), name='disciplina_create'),
    path('disciplinas/<uuid:pk>/', views.DisciplinaDetailView.as_view(), name='disciplina_detail'),
    path('disciplinas/<uuid:pk>/edit/', views.DisciplinaUpdateView.as_view(), name='disciplina_edit'),

    path('topicos/', views.TopicoListView.as_view(), name='topico_list'),
    path('topicos/new/', views.TopicoCreateView.as_view(), name='topico_create'),
    path('topicos/<uuid:pk>/', views.TopicoDetailView.as_view(), name='topico_detail'),
    path('topicos/<uuid:pk>/edit/', views.TopicoUpdateView.as_view(), name='topico_edit'),

    path('questoes/', views.QuestaoListView.as_view(), name='questao_list'),
    path('questoes/new/', views.QuestaoCreateView.as_view(), name='questao_create'),
    path('questoes/<uuid:pk>/', views.QuestaoDetailView.as_view(), name='questao_detail'),
    path('questoes/<uuid:pk>/edit/', views.QuestaoUpdateView.as_view(), name='questao_edit'),
    path('questoes/<uuid:questao_id>/answer/', views.answer_question, name='answer_question'),
]
