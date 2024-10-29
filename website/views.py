# views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from api.models import Banca, Concurso, Disciplina, Topico, Questao, ConcursoTopico
from .forms import BancaForm, ConcursoForm, DisciplinaForm, TopicoForm, QuestaoForm
from django.shortcuts import render
from django.db.models import Count, Avg, Q, F, Max
from datetime import datetime, timedelta
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_POST
import json
from django.views.generic import CreateView, UpdateView
from django.core.paginator import Paginator

# Banca Views
class BancaListView(ListView):
    model = Banca
    template_name = 'bancas/banca_list.html'
    context_object_name = 'bancas'

class BancaDetailView(DetailView):
    model = Banca
    template_name = 'bancas/banca_detail.html'

class BancaCreateView(CreateView):
    model = Banca
    form_class = BancaForm
    template_name = 'bancas/banca_form.html'
    success_url = reverse_lazy('banca_list')

class BancaUpdateView(UpdateView):
    model = Banca
    form_class = BancaForm
    template_name = 'bancas/banca_form.html'
    success_url = reverse_lazy('banca_list')


# Concurso Views
class ConcursoListView(ListView):
    model = Concurso
    template_name = 'concursos/concurso_list.html'
    context_object_name = 'concursos'

class ConcursoDetailView(DetailView):
    model = Concurso
    template_name = 'concursos/concurso_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Initialize disciplinas dictionary to store topics grouped by disciplina
        disciplinas = {}
        
        # Annotate topicos with `total_questoes`, `total_acertos` and select `grupo`
        topicos = (self.object.topico_set
                   .annotate(
                       total_questoes=Count('questao'),
                       total_acertos=Count('questao', filter=Q(questao__acerto=True))
                   )
                   .select_related('disciplina', 'grupo')  # Include related fields
                   .order_by('disciplina__nome', 'grupo__nome', 'nome')  # Sort by disciplina, grupo, and then topico name
                   .all())

        # Group topicos by disciplina
        for topico in topicos:
            disciplina = topico.disciplina

            # Ensure the disciplina exists in the dictionary
            if disciplina not in disciplinas:
                disciplinas[disciplina] = []

            # Append the topico to the correct disciplina
            disciplinas[disciplina].append(topico)
        
        context['disciplinas'] = disciplinas
        return context


class ConcursoCreateView(CreateView):
    model = Concurso
    form_class = ConcursoForm
    template_name = 'concursos/concurso_form.html'
    success_url = reverse_lazy('concurso_list')

    def form_valid(self, form):
        # First save the Concurso instance
        self.object = form.save()
        
        # Get the selected topics from the form
        selected_topicos = form.cleaned_data['topicos']
        
        # Create ConcursoTopico instances for each selected topic
        for topico in selected_topicos:
            ConcursoTopico.objects.create(
                concurso=self.object,
                topico=topico
            )
        
        return super().form_valid(form)

class ConcursoUpdateView(UpdateView):
    model = Concurso
    form_class = ConcursoForm
    template_name = 'concursos/concurso_form.html'
    success_url = reverse_lazy('concurso_list')

    def get_initial(self):
        initial = super().get_initial()
        # Check if there are related Topicos
        if self.object.concursotopico_set.exists():
            # Get the Topico instances if needed
            topicos = self.object.concursotopico_set.all()
            # You can also extract specific information if required
            initial['topicos'] = [topico.topico for topico in topicos]  # Adjust as per your needs
        return initial


    def form_valid(self, form):
        concurso = self.get_object()  # Get the current Concurso instance

        # Get the selected topicos from the form
        selected_topicos = form.cleaned_data['topicos']

        # Clear existing topics not in the selected list
        concurso.concursotopico_set.exclude(topico__in=selected_topicos).delete()

        # Create new ConcursoTopico instances for newly selected topics
        for topico in selected_topicos:
            ConcursoTopico.objects.get_or_create(concurso=concurso, topico=topico)

        return super().form_valid(form)


# Disciplina Views
class DisciplinaListView(ListView):
    model = Disciplina
    template_name = 'disciplinas/disciplina_list.html'
    context_object_name = 'disciplinas'

    def get_queryset(self):
        return (Disciplina.objects
                .annotate(
                    total_topicos=Count('topico'),
                    topicos_estudados=Count('topico', 
                        filter=Q(topico__data_estudo__isnull=False)),
                    percentual_estudado=Coalesce(
                        100.0 * Count('topico', 
                            filter=Q(topico__data_estudo__isnull=False)) /
                        Count('topico'),
                        0.0
                    )
                )
                .all())


class DisciplinaDetailView(DetailView):
    model = Disciplina
    template_name = 'disciplinas/disciplina_detail.html'
    paginate_by = 10  # Number of topics per page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        disciplina = self.object
        
        # Update to paginate topicos
        topicos = (
            disciplina.topico_set
            .annotate(
                total_questoes=Count('questao'),
                questoes_respondidas=Count('questao', 
                    filter=Q(questao__data_realizada__isnull=False)),
                taxa_acerto=Coalesce(
                    100.0 * Count('questao', 
                        filter=Q(questao__acerto=True)) /
                    Count('questao', 
                        filter=Q(questao__data_realizada__isnull=False)),
                    None
                )
            )
            .select_related('grupo')  # Add 'grupo' for efficient querying
            .order_by('grupo__nome', 'nome')  # Sort by grupo name first, then by topico name
            .all()
        )

        # Implement pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(topicos, self.paginate_by)
        paginated_topicos = paginator.get_page(page)

        context['topicos'] = paginated_topicos
        context['page_obj'] = paginated_topicos
        
        # Calculate disciplina statistics
        total_topicos = disciplina.topico_set.count()
        topicos_estudados = disciplina.topico_set.exclude(data_estudo=None).count()
        
        questoes = Questao.objects.filter(topicos__disciplina=disciplina)

        context['stats'] = {
            'total_topicos': total_topicos,
            'topicos_estudados': topicos_estudados,
            'percentual_estudado': (
                (topicos_estudados / total_topicos * 100)
                if total_topicos > 0 else 0
            ),
            'total_questoes': questoes.count(),
            'questoes_respondidas': questoes.exclude(data_realizada=None).count(),
            'taxa_acerto': (
                questoes.filter(acerto=True).count() /
                questoes.exclude(data_realizada=None).count() * 100
                if questoes.exclude(data_realizada=None).exists()
                else 0
            ),
            'topicos_revisar': disciplina.topico_set.filter(
                data_estudo__lt=datetime.now().date() - timedelta(days=90)
            ).count(),
            'ultima_atualizacao': disciplina.topico_set.aggregate(
                last_update=Max('data_estudo')
            )['last_update']
        }

        return context

class DisciplinaCreateView(CreateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'disciplinas/disciplina_form.html'
    success_url = reverse_lazy('disciplina_list')

class DisciplinaUpdateView(UpdateView):
    model = Disciplina
    form_class = DisciplinaForm
    template_name = 'disciplinas/disciplina_form.html'
    success_url = reverse_lazy('disciplina_list')


# Topico Views
class TopicoListView(ListView):
    model = Topico
    template_name = 'topicos/topico_list.html'
    context_object_name = 'disciplinas'  # Changed from 'topicos'

    def get_queryset(self):
        # Get annotated topicos and group them by disciplina
        topicos = (Topico.objects
                .annotate(
                    total_questoes=Count('questao'),
                    total_acertos=Count('questao', filter=Q(questao__acerto=True)),
                    taxa_acerto=Coalesce(
                        100.0 * Count('questao', filter=Q(questao__acerto=True)) /
                        Count('questao'),
                        0.0
                    )
                )
                .select_related('disciplina')
                .order_by('disciplina__nome', 'nome')  # Order by disciplina and then topico name
                .all())
        
        # Group topicos by disciplina
        disciplinas = {}
        for topico in topicos:
            if topico.disciplina not in disciplinas:
                disciplinas[topico.disciplina] = []
            disciplinas[topico.disciplina].append(topico)
            
        return disciplinas


class TopicoDetailView(DetailView):
    model = Topico
    template_name = 'topicos/topico_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the topico object
        topico = self.object
        
        # Add questions related to this topic with their stats
        context['questoes'] = (topico.questao_set
                             .annotate(
                                 banca_nome=F('banca__nome'),
                                 concurso_nome=F('concurso__entidade')
                             )
                             .all())
        
        # Calculate topic statistics
        context['stats'] = {
            'total_questoes': topico.questao_set.count(),
            'questoes_respondidas': topico.questao_set.exclude(data_realizada=None).count(),
            'total_acertos': topico.questao_set.filter(acerto=True).count(),
            'taxa_acerto': (
                topico.questao_set.filter(acerto=True).count() /
                topico.questao_set.exclude(data_realizada=None).count() * 100
                if topico.questao_set.exclude(data_realizada=None).exists()
                else 0
            )
        }
        
        return context


class TopicoCreateView(CreateView):
    model = Topico
    form_class = TopicoForm
    template_name = 'topicos/topico_form.html'
    success_url = reverse_lazy('topico_list')

class TopicoUpdateView(UpdateView):
    model = Topico
    form_class = TopicoForm
    template_name = 'topicos/topico_form.html'
    success_url = reverse_lazy('topico_list')


# Questao Views
class QuestaoListView(ListView):
    model = Questao
    template_name = 'questoes/questao_list.html'
    context_object_name = 'questoes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Questao.objects.all()

        # Define the date three months ago as a date object
        three_months_ago = (timezone.now() - timedelta(days=90)).date()

        # Create a list to hold the IDs of correctly answered questions within the last three months
        recent_correct_answers = []

        for questao in queryset:
            if questao.acerto and questao.data_realizada and questao.data_realizada >= three_months_ago:
                recent_correct_answers.append(questao.id)

        # Store this list in the instance for access in the template
        self.recent_correct_answers = recent_correct_answers

        # Filter by disciplina
        disciplina_id = self.request.GET.get('disciplina')
        if disciplina_id:
            queryset = queryset.filter(topicos__disciplina_id=disciplina_id)

        # Filter by topico
        topico_id = self.request.GET.get('topico')
        if topico_id:
            queryset = queryset.filter(topicos__id=topico_id)

        # Filter by banca
        banca_id = self.request.GET.get('banca')
        if banca_id:
            queryset = queryset.filter(banca_id=banca_id)

        # Filter by status
        status = self.request.GET.get('status')
        if status == 'answered':
            queryset = queryset.filter(data_realizada__isnull=False)
        elif status == 'unanswered':
            queryset = queryset.filter(data_realizada__isnull=True)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Preserve query parameters for pagination
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['query_string'] = query_params.urlencode()
        
        # Add filter options to context
        context['disciplinas'] = Disciplina.objects.all()
        context['bancas'] = Banca.objects.all()
        
        # Get selected disciplina_id
        selected_disciplina_id = self.request.GET.get('disciplina')
        
        # Get topicos based on selected disciplina
        if selected_disciplina_id:
            context['topicos'] = Topico.objects.filter(disciplina_id=selected_disciplina_id)
        else:
            context['topicos'] = Topico.objects.all()
        
        # Add current filter selections to context
        context['current_filters'] = {
            'disciplina': selected_disciplina_id,
            'banca': self.request.GET.get('banca', ''),
            'topico': self.request.GET.get('topico', ''),
            'status': self.request.GET.get('status', '')
        }
        
        return context

class QuestaoDetailView(DetailView):
    model = Questao
    template_name = 'questoes/questao_detail.html'

class QuestaoCreateView(CreateView):
    model = Questao
    form_class = QuestaoForm
    template_name = 'questoes/questao_form.html'
    success_url = reverse_lazy('questao_list')

class QuestaoUpdateView(UpdateView):
    model = Questao
    form_class = QuestaoForm
    template_name = 'questoes/questao_form.html'
    success_url = reverse_lazy('questao_list')

@require_POST
def answer_question(request, questao_id):
    data = json.loads(request.body)
    selected_option = data.get("selected_option")

    try:
        questao = Questao.objects.get(id=questao_id)
        
        # Determine the correct answer by checking each `correta_X` field
        correct_answer = None
        for i in range(1, 6):  # Loop through correta_1 to correta_5
            if getattr(questao, f"correta_{i}"):
                correct_answer = f"correta_{i}"
                break
        
        # Compare selected option with the correct answer
        is_correct = (selected_option == correct_answer)
        
        # Update the question instance with response date and correctness
        questao.data_realizada = timezone.now().date()
        questao.acerto = is_correct
        questao.save()

        # Respond with JSON indicating if the answer was correct and updated values
        return JsonResponse({
            "correct": is_correct,
            "data_realizada": questao.data_realizada.strftime('%d/%m/%Y'),
            "acerto": questao.acerto,
        })

    except Questao.DoesNotExist:
        return JsonResponse({"error": "Questão not found."}, status=404)


def index(request):
    # Calculate statistics
    hoje = datetime.now().date()
    tres_meses_atras = hoje - timedelta(days=90)

    # Calculate the success rate, handling the case where no answers are available
    taxa_acerto_aggregate = Questao.objects.exclude(data_realizada=None).aggregate(taxa=Avg('acerto'))
    taxa_acerto = taxa_acerto_aggregate['taxa']
    if taxa_acerto is not None:
        taxa_acerto = round(taxa_acerto * 100)
    else:
        taxa_acerto = 0

    context = {
        # Count active competitions (not finished and with future test date)
        'concursos_ativos': Concurso.objects.filter(
            finalizado=False,
            data_prova__gte=hoje
        ).count(),

        # Count studied topics (with study date)
        'topicos_estudados': Topico.objects.exclude(
            data_estudo=None
        ).count(),

        # Count answered questions
        'questoes_respondidas': Questao.objects.exclude(
            data_realizada=None
        ).count(),

        # Set calculated success rate
        'taxa_acerto': taxa_acerto,

        # Get topics to review (studied more than 3 months ago)
        'topicos_revisar': Topico.objects.filter(
            data_estudo__lt=tres_meses_atras
        ).order_by('data_estudo')[:5],

        # Get upcoming competitions with specific conditions and sort by data_prova
        'concursos_proximos': Concurso.objects.filter(
            iniciado=True,
            inscrito=True,
            finalizado=False
        ).order_by('data_prova')[:5],

    }

    return render(request, 'index.html', context)
