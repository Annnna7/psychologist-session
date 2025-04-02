import sys
from os.path import abspath, dirname
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Добавляем путь к проекту в PYTHONPATH
sys.path.insert(0, dirname(dirname(abspath(__file__))))

# Эти импорты должны быть после добавления пути в sys.path
from App.DataBase.base import Base
from App.DataBase.models.user import User  # Явный импорт всех моделей
from App.DataBase.models.psychologist import Psychologist
from App.DataBase.models.bracelet import Bracelet
from App.DataBase.models.session import Session
from App.DataBase.models.notification import Notification

# Это важно для autogenerate
target_metadata = Base.metadata

# Конфигурация логгера (обычно уже есть в сгенерированном файле)
fileConfig(context.config.config_file_name)

def run_migrations_offline():
    """Запуск миграций в offline-режиме."""
    url = context.config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Запуск миграций в online-режиме."""
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=True  # Если используете схемы
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()