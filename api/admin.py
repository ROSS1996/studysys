# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import (
    Banca, Concurso, Disciplina, Topico, ConcursoTopico, GrupoTopico,
    Questao, QuestaoTopico
)


@admin.register(Banca)
class BancaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'total_concursos', 'total_questoes')
    search_fields = ('nome',)
    ordering = ('nome',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            total_concursos=Count('concurso', distinct=True),
            total_questoes=Count('questao', distinct=True)
        )

    def total_concursos(self, obj):
        return obj.total_concursos
    total_concursos.short_description = 'Total de Concursos'
    total_concursos.admin_order_field = 'total_concursos'

    def total_questoes(self, obj):
        return obj.total_questoes
    total_questoes.short_description = 'Total de Questões'
    total_questoes.admin_order_field = 'total_questoes'


class ConcursoTopicoInline(admin.TabularInline):
    model = ConcursoTopico
    extra = 1
    autocomplete_fields = ['topico']


class QuestaoTopicoInline(admin.TabularInline):
    model = QuestaoTopico
    extra = 1
    autocomplete_fields = ['topico']


@admin.register(Concurso)
class ConcursoAdmin(admin.ModelAdmin):
    list_display = ('entidade', 'cargo', 'banca', 'data_prova', 'salario_formatado',
                   'nivel', 'status_badge', 'inscrito')
    list_filter = ('banca', 'nivel', 'inscrito', 'iniciado', 'finalizado')
    search_fields = ('entidade', 'cargo')
    date_hierarchy = 'data_prova'
    ordering = ('-data_prova',)
    inlines = [ConcursoTopicoInline]
    actions = ['marcar_como_inscrito', 'marcar_como_iniciado', 'marcar_como_finalizado']

    def salario_formatado(self, obj):
        return f'R$ {obj.salario:,.2f}'.replace(',', '.')
    salario_formatado.short_description = 'Salário'
    salario_formatado.admin_order_field = 'salario'

    def status_badge(self, obj):
        if obj.finalizado:
            color = 'green'
            status = 'Finalizado'
        elif obj.iniciado:
            color = 'orange'
            status = 'Em andamento'
        else:
            color = 'gray'
            status = 'Não iniciado'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>',
            color, status
        )
    status_badge.short_description = 'Status'

    def marcar_como_inscrito(self, request, queryset):
        queryset.update(inscrito=True)
    marcar_como_inscrito.short_description = "Marcar selecionados como inscrito"

    def marcar_como_iniciado(self, request, queryset):
        queryset.update(iniciado=True)
    marcar_como_iniciado.short_description = "Marcar selecionados como iniciado"

    def marcar_como_finalizado(self, request, queryset):
        queryset.update(finalizado=True)
    marcar_como_finalizado.short_description = "Marcar selecionados como finalizado"

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('entidade', 'cargo', 'banca', 'area', 'edital')
        }),
        ('Datas e Status', {
            'fields': ('data_abertura', 'data_prova', 'iniciado', 'finalizado', 'inscrito')
        }),
        ('Informações Adicionais', {
            'fields': ('salario', 'nivel')
        })
    )


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'total_topicos')
    search_fields = ('nome',)
    ordering = ('nome',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_topicos=Count('topico'))

    def total_topicos(self, obj):
        return obj.total_topicos
    total_topicos.short_description = 'Total de Tópicos'
    total_topicos.admin_order_field = 'total_topicos'

@admin.register(GrupoTopico)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'id', 'total_topicos')
    search_fields = ('nome',)
    ordering = ('nome',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_topicos=Count('topico'))

    def total_topicos(self, obj):
        return obj.total_topicos
    total_topicos.short_description = 'Total de Tópicos'
    total_topicos.admin_order_field = 'total_topicos'

@admin.register(Topico)
class TopicoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'disciplina', 'grupo', 'data_estudo', 'total_questoes')
    list_filter = ('data_estudo', 'disciplina', 'grupo')
    search_fields = ('nome',)
    ordering = ('nome',)
    date_hierarchy = 'data_estudo'
    autocomplete_fields = ['disciplina', 'grupo']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            total_questoes=Count('questaotopico', distinct=True)
        )

    def total_questoes(self, obj):
        return obj.total_questoes
    total_questoes.short_description = 'Total de Questões'
    total_questoes.admin_order_field = 'total_questoes'


@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'banca', 'concurso', 'get_enunciado_preview',
                   'resultado_badge', 'data_realizada')
    list_filter = ('banca', 'concurso', 'acerto', 'data_realizada', 'topicos')
    search_fields = ('enunciado', 'banca__nome', 'concurso__entidade')
    inlines = [QuestaoTopicoInline]
    date_hierarchy = 'data_realizada'

    def get_enunciado_preview(self, obj):
        return obj.enunciado[:100] + '...' if len(obj.enunciado) > 100 else obj.enunciado
    get_enunciado_preview.short_description = 'Enunciado'

    def resultado_badge(self, obj):
        if obj.acerto is None:
            color = 'gray'
            status = 'Não respondida'
        elif obj.acerto:
            color = 'green'
            status = 'Acerto'
        else:
            color = 'red'
            status = 'Erro'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 7px; border-radius: 3px;">{}</span>',
            color, status
        )
    resultado_badge.short_description = 'Resultado'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('banca', 'concurso', 'enunciado')
        }),
        ('Alternativas', {
            'fields': (
                ('alternativa_1', 'correta_1'),
                ('alternativa_2', 'correta_2'),
                ('alternativa_3', 'correta_3'),
                ('alternativa_4', 'correta_4'),
                ('alternativa_5', 'correta_5'),
            )
        }),
        ('Resultado', {
            'fields': ('acerto', 'data_realizada', 'anulada')
        })
    )
