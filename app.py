from flask import Flask, render_template, request, redirect, url_for
from models import db, Denuncia
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
import time
import os

app = Flask(__name__, 
    template_folder='templates',  # Especificamos la carpeta de templates
    static_folder='static'        # Especificamos la carpeta de archivos estáticos
)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///denuncias.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar la base de datos
db.init_app(app)

# Crear todas las tablas
with app.app_context():
    db.create_all()

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