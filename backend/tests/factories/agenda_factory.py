import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('pt_BR')

try:
    from app.models.agenda import EventoAgenda
    from app.models.usuario import Usuario
    from app.models.cliente import Cliente
    from app.models.ordem_servico import OrdemServico
except ImportError:
    # Models podem não existir ainda - serão criados quando necessário
    pass


class EventoAgendaFactory(SQLAlchemyModelFactory):
    """Factory para EventoAgenda."""
    
    class Meta:
        model = EventoAgenda
        sqlalchemy_session_persistence = 'commit'

    titulo = factory.LazyFunction(lambda: fake.sentence(nb_words=3))
    descricao = factory.LazyFunction(lambda: fake.sentence(nb_words=10))
    tipo_evento = factory.Iterator(['visita', 'manutencao', 'instalacao', 'reparo', 'outro'])
    
    # Data e hora (hoje ou amanhã)
    data_inicio = factory.LazyFunction(lambda: datetime.now() + timedelta(hours=fake.random_int(min=1, max=24)))
    data_fim = factory.LazyAttribute(lambda obj: obj.data_inicio + timedelta(hours=fake.random_int(min=1, max=4)))
    
    # Localização
    endereco = factory.LazyFunction(lambda: fake.address())
    latitude = factory.LazyFunction(lambda: fake.latitude())
    longitude = factory.LazyFunction(lambda: fake.longitude())
    
    status = factory.Iterator(['agendado', 'em_andamento', 'concluido', 'cancelado'])
    observacao = factory.LazyFunction(lambda: fake.sentence(nb_words=8))

    @factory.post_generation
    def tecnico(self, create, extracted, **kwargs):
        if extracted:
            self.tecnico_id = extracted.id

    @factory.post_generation
    def cliente(self, create, extracted, **kwargs):
        if extracted:
            self.cliente_id = extracted.id

    @factory.post_generation
    def ordem_servico(self, create, extracted, **kwargs):
        if extracted:
            self.ordem_servico_id = extracted.id
