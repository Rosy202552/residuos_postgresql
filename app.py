from flask import Flask, render_template, request, redirect, url_for
from models import db, Denuncia
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
import time
import os
from urllib.parse import urlsplit, urlunsplit, quote_plus

app = Flask(__name__,
    template_folder='templates',  # Especificamos la carpeta de templates
    static_folder='static'        # Especificamos la carpeta de archivos estáticos
)

# Configuración de la base de datos
# Tomamos la URL de conexión desde la variable de entorno DATABASE_URL si existe.
# Para evitar errores con caracteres no ASCII en usuario/contraseña (por ejemplo 'ó'),
# hacemos un parse y percent-encode de esas partes.
raw_db_url = os.environ.get('DATABASE_URL')
if raw_db_url:
    try:
        parts = urlsplit(raw_db_url)
        if parts.username or parts.password:
            user = quote_plus(parts.username) if parts.username else ''
            pwd = quote_plus(parts.password) if parts.password else ''
            netloc = ''
            if user:
                netloc += user
                if pwd:
                    netloc += ':' + pwd
                netloc += '@'
            hostport = parts.hostname or ''
            if parts.port:
                hostport += f":{parts.port}"
            netloc += hostport
            safe_db_url = urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))
        else:
            safe_db_url = raw_db_url
    except Exception:
        # Si falla el parse por cualquier razón, usamos la raw URL (la excepción
        # será más informativa en el intento de conexión).
        safe_db_url = raw_db_url
    app.config['SQLALCHEMY_DATABASE_URI'] = safe_db_url
else:
    # Fallback local para desarrollo: sqlite en carpeta instance
    # Asegurarnos de que la carpeta instance existe y usar una ruta absoluta
    instance_dir = os.path.join(app.root_path, 'instance')
    try:
        os.makedirs(instance_dir, exist_ok=True)
    except Exception:
        # si no podemos crear el directorio, seguiremos y permitiremos que SQLite falle
        pass
    sqlite_path = os.path.join(instance_dir, 'app.db')
    # En Windows, SQLAlchemy funciona mejor con forward slashes en la URI
    sqlite_uri = 'sqlite:///' + os.path.abspath(sqlite_path).replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)
# Inicializar Flask-Migrate (maneja migraciones con Alembic)
migrate = Migrate(app, db)

# NOTA: No ejecutamos `db.create_all()` automáticamente al importar la app.
# Usar migraciones (Flask-Migrate / Alembic) para aplicar cambios de esquema
# en entornos de desarrollo y producción. Para operaciones puntuales puedes usar
# `python manage.py upgrade` o, si realmente lo necesitas, ejecutar manualmente
# `db.create_all()` dentro de un contexto de app desde una consola.

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/introduccion')
def introduccion():
    return render_template('introduccion.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')

@app.route('/juego')
def juego():
    return render_template('juego.html')

# CRUD de denuncias
@app.route('/denuncias', methods=['GET', 'POST'])
def denuncias():
    if request.method == 'POST':
        nombre = request.form['nombre'] or "Anónimo"
        lugar = request.form['lugar']

        # Estrategia: crear la denuncia con un número temporal único (negativo basado en timestamp),
        # commitear para obtener el id autoincremental, y luego asignar numero = id.
        # Esto evita modificar el esquema de la base de datos actual y preserva datos existentes.
        temp_num = -int(time.time() * 1000)
        nueva = Denuncia(numero=temp_num, nombre=nombre, lugar=lugar)
        db.session.add(nueva)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Si por alguna razón el número temporal colisiona (improbable), generar otro y reintentar una vez
            temp_num = -int(time.time() * 1000)
            nueva.numero = temp_num
            db.session.add(nueva)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                return redirect(url_for('denuncias'))

        # Ahora asignamos numero = id (valor autoincremental) y guardamos de nuevo
        try:
            nueva.numero = nueva.id
            db.session.add(nueva)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Si por alguna razón existe conflicto al asignar id (muy improbable), dejamos el número temporal y redirigimos
            return redirect(url_for('denuncias'))
        return redirect(url_for('denuncias'))
    denuncias = Denuncia.query.all()
    return render_template('denuncias.html', denuncias=denuncias)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    denuncia = Denuncia.query.get_or_404(id)
    if request.method == 'POST':
        denuncia.nombre = request.form['nombre'] or "Anónimo"
        denuncia.lugar = request.form['lugar']
        db.session.commit()
        return redirect(url_for('denuncias'))
    return render_template('editar_denuncia.html', denuncia=denuncia)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    denuncia = Denuncia.query.get_or_404(id)
    db.session.delete(denuncia)
    db.session.commit()
    return redirect(url_for('denuncias'))

if __name__ == '__main__':
    app.run(debug=True)