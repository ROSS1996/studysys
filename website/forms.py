# forms.py
from django import forms
from api.models import Banca, Concurso, Disciplina, Topico, Questao
from django.db.models import F

class BancaForm(forms.ModelForm):
    class Meta:
        model = Banca
        fields = ['nome']

class TopicCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value and value.instance:
            topic = value.instance
            option['label'] = f"{topic.disciplina.nome} - {topic.nome}"
        return option

class ConcursoForm(forms.ModelForm):
    topicos = forms.ModelMultipleChoiceField(
        queryset=Topico.objects.none(),
        widget=TopicCheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
        required=False
    )

    class Meta:
        model = Concurso
        fields = [
            'entidade', 'cargo', 'banca', 'data_abertura', 'salario', 
            'nivel', 'data_prova', 'area', 'iniciado', 'finalizado', 
            'inscrito', 'topicos'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            # Set the queryset for topicos
            # First annotate with disciplina name, then order by disciplina and topic name
            self.fields['topicos'].queryset = (
                Topico.objects
                .select_related('disciplina')  # Optimize by pre-fetching disciplina
                .order_by('disciplina__nome', 'nome')
            )


class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome']

class TopicoForm(forms.ModelForm):
    class Meta:
        model = Topico
        fields = ['nome', 'disciplina', 'grupo', 'data_estudo']

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = [
            'banca', 'concurso', 'enunciado', 'alternativa_1', 
            'correta_1', 'alternativa_2', 'correta_2', 'alternativa_3', 
            'correta_3', 'alternativa_4', 'correta_4', 'alternativa_5', 
            'correta_5', 'topicos', 'data_realizada', 'acerto', 'anulada'
        ]
