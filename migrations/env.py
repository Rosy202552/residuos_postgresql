from __future__ import with_statement
from alembic import context
from logging.config import fileConfig
from sqlalchemy import pool, create_engine

# Import the Flask app and the SQLAlchemy `db` from the project
from app import app as flask_app
from models import db as models_db

# Alembic config
config = context.config
try:
    if config.config_file_name:
        fileConfig(config.config_file_name)
except Exception:
    pass

target_metadata = models_db.metadata

def run_migrations_offline():
    url = str(flask_app.config.get('SQLALCHEMY_DATABASE_URI'))
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Crear un engine directamente desde la URL de la app para evitar problemas
    # con la obtención del engine desde Flask-SQLAlchemy en este contexto.
    url = str(flask_app.config.get('SQLALCHEMY_DATABASE_URI'))
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
