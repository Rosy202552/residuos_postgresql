import os
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_migrate import init as fm_init, migrate as fm_migrate, upgrade as fm_upgrade, revision as fm_revision, stamp as fm_stamp

# Import the app factory / app instance
from app import app, db


@click.group()
def cli():
    """Comandos de utilidad para el proyecto."""
    pass


@cli.command('init')
@with_appcontext
def init_migrations():
    """Inicializa el directorio de migraciones (alembic)."""
    fm_init()
    click.echo('Directorio de migraciones inicializado.')


@cli.command('migrate')
@click.option('-m', '--message', default='migration', help='Mensaje para la migración')
@with_appcontext
def migrate(message):
    """Crear una nueva migración basada en los modelos actuales."""
    fm_migrate(message=message)
    click.echo(f'Migración creada: {message}')


@cli.command('upgrade')
@with_appcontext
def upgrade():
    """Aplicar migraciones pendientes a la base de datos."""
    fm_upgrade()
    click.echo('Base de datos actualizada (upgrade).')


@cli.command('revision')
@click.option('-m', '--message', default='revision', help='Mensaje para la revisión')
@with_appcontext
def revision(message):
    """Crear una migración vacía (autogenerada opcionalmente)."""
    fm_revision(message=message)
    click.echo(f'Revision creada: {message}')


@cli.command('stamp')
@click.option('--rev', default='head', help='Revision a marcar')
@with_appcontext
def stamp(rev):
    """Marcar la base de datos con una revisión (sin ejecutar migraciones)."""
    fm_stamp(rev)
    click.echo(f'DB marcada en revision: {rev}')


@cli.command('run')
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=5000, type=int)
def run(host, port):
    """Arranca la app con el servidor de desarrollo (no recomendable en producción)."""
    app.run(host=host, port=port, debug=app.debug)


@cli.command('shell')
def shell():
    """Abre una shell de Python con el contexto de la app y db cargados."""
    import code
    ctx = {'app': app, 'db': db}
    code.interact(local=ctx)


if __name__ == '__main__':
    cli()
