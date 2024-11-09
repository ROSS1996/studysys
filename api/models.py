import uuid
from django.db import models
from django.core.exceptions import ValidationError

NIVEL_CHOICES = [
    ('Fundamental', 'Fundamental'),
    ('Médio', 'Médio'),
    ('Superior', 'Superior'),
]


class Banca(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome


class Concurso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entidade = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    banca = models.ForeignKey(Banca, on_delete=models.SET_NULL, null=True)
    data_abertura = models.DateField()
    salario = models.BigIntegerField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    data_prova = models.DateField()
    area = models.CharField(max_length=255, null=True, blank=True)
    edital = models.URLField(max_length=255, null=True, blank=True)
    iniciado = models.BooleanField(default=False)
    finalizado = models.BooleanField(default=False)
    inscrito = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.entidade} - {self.cargo}"


class Disciplina(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class GrupoTopico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

class Topico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)  # Updated field
    grupo = models.ForeignKey(GrupoTopico, on_delete=models.CASCADE, null=True, blank=True)  # Updated field
    concursos = models.ManyToManyField(Concurso, through='ConcursoTopico')
    data_estudo = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nome


class ConcursoTopico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    concurso = models.ForeignKey(Concurso, on_delete=models.CASCADE)
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE)


class Questao(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    banca = models.ForeignKey(Banca, on_delete=models.SET_NULL, null=True)
    concurso = models.ForeignKey(Concurso, on_delete=models.SET_NULL, null=True)
    enunciado = models.TextField()
    
    # Define alternativas 1 e 2 como obrigatórias e 3, 4, e 5 como opcionais
    alternativa_1 = models.TextField(default='Verdadeiro')
    alternativa_2 = models.TextField(default='Falso')
    alternativa_3 = models.TextField(null=True, blank=True)
    alternativa_4 = models.TextField(null=True, blank=True)
    alternativa_5 = models.TextField(null=True, blank=True)
    
    # Nova implementação dos campos correta e resposta
    correta = models.IntegerField(default=1)
    resposta = models.IntegerField(null=True, blank=True)

    # Campo opcional de resolução
    resolucao = models.TextField(null=True, blank=True)

    topicos = models.ManyToManyField(Topico, through='QuestaoTopico')
    data_realizada = models.DateField(null=True, blank=True)
    anulada = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Questão {self.id}"

    def clean(self):
        # Valida que a resposta e correta estejam em 1-5, se fornecidas
        if self.correta is not None and not (1 <= self.correta <= 5):
            raise ValidationError('O campo correta deve ser um número entre 1 e 5.')
        
        if self.resposta is not None and not (1 <= self.resposta <= 5):
            raise ValidationError('O campo resposta deve ser um número entre 1 e 5.')
        
        # Valida que a resposta correta não aponte para uma alternativa nula ou vazia
        alternativas = [
            self.alternativa_1,
            self.alternativa_2,
            self.alternativa_3,
            self.alternativa_4,
            self.alternativa_5,
        ]
        
        if self.correta is not None and not alternativas[self.correta - 1]:
            raise ValidationError(f'A alternativa {self.correta} está vazia, portanto não pode ser a correta.')
        
        if self.resposta is not None and not alternativas[self.resposta - 1]:
            raise ValidationError(f'A alternativa {self.resposta} está vazia, portanto não pode ser a resposta.')
        
        # Valida que as alternativas não "pulem" posições
        for i in range(2, 5):
            if alternativas[i] and not alternativas[i - 1]:
                raise ValidationError(f'Alternativa {i + 1} não pode estar preenchida se a alternativa {i} está vazia.')

class QuestaoTopico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE)
