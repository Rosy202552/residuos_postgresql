# Despliegue y migraciones

Este proyecto usa Flask + Flask-SQLAlchemy. Para evitar pérdida de datos en producción (por ejemplo en Render), recomendamos usar migraciones con Flask-Migrate (Alembic) en lugar de `db.create_all()` contra la base de datos remota.

Resumen de cambios realizados localmente:
- `app.py` ahora inicializa `Flask-Migrate`.
- `create_all()` se ejecuta automáticamente sólo para el fallback local SQLite; si `DATABASE_URL` está presente, `create_all()` se omite por seguridad.

Dependencias agregadas en `requirements.txt`:
- `Flask-Migrate`
- `psycopg2-binary` (driver PostgreSQL)
- `python-dotenv` (opcional, para cargar `.env` en desarrollo)

Instrucciones rápidas (desarrollo local con PowerShell)

1) Instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

2) Usar SQLite local por defecto (si no tienes DATABASE_URL):

```powershell
python -c "import app; print('app import OK')"
```

3) Para usar PostgreSQL local/Remoto con `DATABASE_URL`, exporta la variable de entorno (PowerShell):

```powershell
$env:DATABASE_URL = 'postgresql://usuario:password@host:5432/nombredb'
```

4) Inicializar migraciones (sólo una vez por proyecto):

```powershell
# establece la app para la CLI de Flask
$env:FLASK_APP = 'app.py'
# inicializa el directorio de migraciones (ejecutar sólo la primera vez)
flask db init
# crear una migración con los modelos actuales
flask db migrate -m "create initial tables"
# aplicar la migración a la base de datos
flask db upgrade
```

En Render (producción)

- Añade la variable de entorno `DATABASE_URL` en el dashboard de tu servicio en Render.
- En la sección "Build or Deploy Command" o en la configuración, ejecuta las migraciones durante el deploy, por ejemplo:

```text
pip install -r requirements.txt; flask db upgrade
```

- Asegúrate de que el `start command` use gunicorn o tu preferencia, p. ej.: `gunicorn app:app`.

Nota sobre tu base de datos en Render

Según indicas, tu base de datos en Render se llama `denuncias`. La `DATABASE_URL` debe apuntar a esa base de datos.
Ejemplo (rellena usuario, contraseña y host que Render te proporcione):

```text
postgresql://<usuario>:<password>@<host>:5432/denuncias
```

Ejemplo de flujo de deploy en Render (Build Command):

```text
pip install -r requirements.txt; flask db upgrade
```

Y asegurarte de que en Environment > Environment Variables tengas:
- `DATABASE_URL` = `postgresql://.../denuncias`
- (opcional) `INIT_DB` = `1` si de verdad quieres forzar `create_all()` (no recomendado)

Con esto, las migraciones (`flask db upgrade`) aplicarán los cambios a la base `denuncias` y no se perderán los datos que ya existan.

Notas de seguridad

- No uses `db.create_all()` contra la base de datos remota en producción: puede causar inconsistencias con esquemas existentes. Siempre usa migraciones controladas (`flask db migrate` + `flask db upgrade`).
- Evita exponer contraseñas en logs. Si tu contraseña contiene caracteres especiales o acentos, o si obtienes errores de codificación, usa percent-encoding o variables separadas; `app.py` hace un percent-encode básico de usuario/contraseña cuando detecta `DATABASE_URL`.

Si quieres, puedo:
- Añadir el directorio `migrations/` inicial (ejecutando `flask db init` aquí y crear la migración inicial). Necesitaré permiso para crear esos archivos en el repo.
- Añadir un pequeño script `manage.py` para facilitar comandos de migración.
- Configurar `python-dotenv` para cargar `.env` en desarrollo automáticamente.
