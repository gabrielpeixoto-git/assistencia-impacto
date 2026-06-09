import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('pt_BR')

try:
    from app.models.usuario import Usuario, Perfil
    from app.core.seguranca import hash_senha
except ImportError:
    # Models podem não existir ainda - serão criados quando necessário
    pass


class UsuarioFactory(SQLAlchemyModelFactory):
    """Factory para Usuario."""
    
    class Meta:
        model = Usuario
        sqlalchemy_session_persistence = 'commit'

    email = factory.LazyFunction(lambda: fake.email())
    senha_hash = factory.LazyFunction(lambda: hash_senha("Senha123!"))
    nome_completo = factory.LazyFunction(lambda: fake.name())
    telefone = factory.LazyFunction(lambda: fake.phone_number())
    perfil = factory.Iterator([Perfil.ADMIN, Perfil.GERENTE, Perfil.TECNICO, Perfil.VISUALIZADOR])
    ativo = True


class TecnicoFactory(UsuarioFactory):
    """Factory específica para técnicos."""
    
    perfil = Perfil.TECNICO
    
    @factory.post_generation
    def especialidades(self, create, extracted, **kwargs):
        """Adiciona especialidades ao técnico."""
        if extracted:
            self.especialidades = extracted
        else:
            self.especialidades = ['eletrica', 'hidraulica']


class AdminFactory(UsuarioFactory):
    """Factory específica para administradores."""
    
    perfil = Perfil.ADMIN


class GerenteFactory(UsuarioFactory):
    """Factory específica para gerentes."""
    
    perfil = Perfil.GERENTE
