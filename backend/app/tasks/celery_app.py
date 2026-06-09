from celery import Celery
from app.config import settings

# Criar aplicação Celery
celery_app = Celery(
    "assistencia_impacto",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.whatsapp_tasks",
        "app.tasks.pdf_tasks",
    ]
)

# Configurações do Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configurações de retry
celery_app.conf.update(
    task_default_retry_delay=60,  # 60 segundos
    task_max_retries=3,
)

# Configurações de beat para tarefas agendadas
celery_app.conf.beat_schedule = {
    "verificar-notificacoes-pendentes": {
        "task": "app.tasks.email_tasks.verificar_notificacoes_pendentes",
        "schedule": 300.0,  # 5 minutos
    },
    "verificar-os-agendadas": {
        "task": "app.tasks.whatsapp_tasks.verificar_os_agendadas",
        "schedule": 600.0,  # 10 minutos
    },
}
