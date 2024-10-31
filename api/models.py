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
    
    # Make alternativas mandatory
    alternativa_1 = models.TextField(default='Verdadeiro')
    correta_1 = models.BooleanField(default=True)
    alternativa_2 = models.TextField(default='Falso')
    correta_2 = models.BooleanField(default=False)
    
    # Alternativas 3, 4, 5 are optional and correspond to optional corretas
    alternativa_3 = models.TextField(null=True, blank=True)
    correta_3 = models.BooleanField(blank=True)
    alternativa_4 = models.TextField(null=True, blank=True)
    correta_4 = models.BooleanField(blank=True)
    alternativa_5 = models.TextField(null=True, blank=True)
    correta_5 = models.BooleanField(blank=True)

    topicos = models.ManyToManyField(Topico, through='QuestaoTopico')
    data_realizada = models.DateField(null=True, blank=True)
    acerto = models.BooleanField(null=True, blank=True)
    anulada = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"Questão {self.id}"

    def clean(self):
        # Validate alternativas and corretas
        if not self.alternativa_1 and self.correta_1:
            raise ValidationError('Alternativa 1 must not be empty if correta 1 is True.')
        
        if not self.alternativa_2 and self.correta_2:
            raise ValidationError('Alternativa 2 must not be empty if correta 2 is True.')

        # Ensure at least one correta is True
        corretas = [self.correta_1, self.correta_2, self.correta_3, self.correta_4, self.correta_5]
        if not any(corretas):
            raise ValidationError('At least one correta must be True.')
        
        # Ensure no more than one correta is True
        if corretas.count(True) > 1:
            raise ValidationError('Only one question can be True.')

        # Check that if alternatives 3, 4, or 5 are empty, their corretas must also be None
        if not self.alternativa_3 and self.correta_3 is True:
            raise ValidationError('Correta 3 cannot be set if Alternativa 3 is empty.')
        
        if not self.alternativa_4 and self.correta_4 is True:
            raise ValidationError('Correta 4 cannot be set if Alternativa 4 is empty.')
        
        if not self.alternativa_5 and self.correta_5 is True:
            raise ValidationError('Correta 5 cannot be set if Alternativa 5 is empty.')



class QuestaoTopico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE)
