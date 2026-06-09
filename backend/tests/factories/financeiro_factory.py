import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('pt_BR')

try:
    from app.models.financeiro import Transacao, CategoriaFinanceira
    from app.models.usuario import Usuario
except ImportError:
    # Models podem não existir ainda - serão criados quando necessário
    pass


class CategoriaFinanceiraFactory(SQLAlchemyModelFactory):
    """Factory para CategoriaFinanceira."""
    
    class Meta:
        model = CategoriaFinanceira
        sqlalchemy_session_persistence = 'commit'

    nome = factory.LazyFunction(lambda: fake.word())
    tipo = factory.Iterator(['receita', 'despesa'])
    cor = factory.LazyFunction(lambda: fake.hex_color())
    icone = 'dollar-sign'
    ativo = True


class TransacaoFactory(SQLAlchemyModelFactory):
    """Factory para Transacao."""
    
    class Meta:
        model = Transacao
        sqlalchemy_session_persistence = 'commit'

    tipo = factory.Iterator(['receita', 'despesa'])
    descricao = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    valor = factory.LazyFunction(lambda: fake.random_int(min=5000, max=500000))  # centavos
    data_vencimento = factory.LazyFunction(lambda: fake.future_date(end_date=+30))
    status = 'pendente'
    forma_pagamento = factory.Iterator(['pix', 'dinheiro', 'cartao_credito', 'cartao_debito'])
    observacao = factory.LazyFunction(lambda: fake.sentence(nb_words=8))

    @factory.post_generation
    def categoria(self, create, extracted, **kwargs):
        if extracted:
            self.categoria_id = extracted.id
        elif create:
            cat = CategoriaFinanceiraFactory(tipo=self.tipo)
            self.categoria_id = cat.id

    @factory.post_generation
    def usuario(self, create, extracted, **kwargs):
        if extracted:
            self.usuario_id = extracted.id
