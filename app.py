from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- BASE DE DATOS ----------
def get_db():
    conn = sqlite3.connect('tattoo_forms.db')
    return conn

# Crear tabla si no existe
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS formularios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            sitio TEXT,
            tamanio TEXT,
            disponibilidad TEXT,
            referencias_texto TEXT,
            fotos TEXT,
            forma_contacto TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- FORMULARIO ----------
class FormularioTattoo(FlaskForm):
    nombre = StringField('Nombre y Apellidos', validators=[DataRequired()])
    sitio = StringField('Zona del cuerpo', validators=[DataRequired()])
    foto = FileField('Imagen de referencia', render_kw={"multiple": True})
    tamanio = StringField('Tamaño (cm)', validators=[DataRequired()])
    referencias_texto = TextAreaField('Ideas, referencias y estilo', validators=[DataRequired()])
    disponibilidad = SelectMultipleField('Días preferentes', choices=[
        ('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'),
        ('Jueves', 'Jueves'), ('Viernes', 'Viernes'), ('Sábado', 'Sábado')],
        validators=[DataRequired()])
    disponibilidad_horaria = SelectMultipleField('Disponibilidad horaria', choices=[
        ('Mañanas', 'Mañanas'), ('Tardes', 'Tardes')],
        validators=[DataRequired()])
    
    # Campo para forma de contacto
    forma_contacto = StringField('Forma de contacto (correo o teléfono)', validators=[DataRequired()])

# ---------- RUTAS ----------
@app.route('/')
def index():
    app.logger.info("Accediendo a la página de inicio")
    return redirect(url_for('formulario'))

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = FormularioTattoo()
    if form.validate_on_submit():
        nombre = form.nombre.data
        sitio = form.sitio.data
        tamanio = form.tamanio.data
        disponibilidad = ', '.join(form.disponibilidad.data)  # Almacenamos los días seleccionados
        disponibilidad_horaria = ', '.join(form.disponibilidad_horaria.data)  # Almacenamos los horarios seleccionados
        referencias_texto = form.referencias_texto.data
        forma_contacto = form.forma_contacto.data

        # Guardar archivos
        fotos = form.foto.data
        filenames = []
        if fotos:
            for foto in fotos:
                filename = secure_filename(foto.filename)
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)

        conn = get_db()
        c = conn.cursor()
        c.execute(""" 
            INSERT INTO formularios (nombre, sitio, tamanio, disponibilidad, referencias_texto, fotos, forma_contacto)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (nombre, sitio, tamanio, disponibilidad, referencias_texto, ','.join(filenames), forma_contacto))  # Guardamos los datos
        conn.commit()
        conn.close()

        return redirect(url_for('formulario'))

    return render_template('formulario.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '12345':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return 'Credenciales incorrectas'
    return render_template('login.html')

@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM formularios")
    formularios = c.fetchall()
    conn.close()
    return render_template('admin.html', formularios=formularios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
