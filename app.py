from flask import Flask, render_template, request, redirect, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'ELIGE TU CONTRASEÑA'  # Cámbiala por una clave segura

USUARIOS_FILE = 'usuarios.json'
CITAS_FILE = 'citas.json'


# Función para obtener el usuario actual desde la sesión
def usuario_actual():
    return session.get("usuario")


# Función para cargar datos desde un archivo JSON de forma segura
def cargar_json(file):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Si hay doble corchete, se corrige automáticamente
            if isinstance(data, list) and len(data) == 1 and isinstance(data[0], list):
                data = data[0]

            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Página de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print(request.form)  # Para depuración
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")

        usuarios = cargar_json(USUARIOS_FILE)
        user = next((u for u in usuarios if u.get("usuario") == usuario and u.get("contrasena") == contrasena), None)

        if user:
            session["usuario"] = usuario
            flash("Sesión iniciada", "success")
            return redirect("/")
        else:
            flash("Credenciales incorrectas", "danger")

    return render_template("login.html")


# Página de registro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        contrasena = request.form.get("contrasena")
        usuarios = cargar_json(USUARIOS_FILE)

        if any(u.get("usuario") == usuario for u in usuarios):
            flash("El usuario ya existe", "danger")
            return redirect("/register")

        usuarios.append({"usuario": usuario, "contrasena": contrasena})
        with open(USUARIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)

        flash("Usuario registrado con éxito", "success")
        return redirect("/login")

    return render_template("register.html")


# Página de inicio (panel de citas)
@app.route("/")
def index():
    asegurar_archivos()
    if "usuario" not in session:
        return redirect("/login")

    citas = cargar_json(CITAS_FILE)
    usuario = session["usuario"]
    citas_usuario = [c for c in citas if c.get("usuario") == usuario]
    citas_usuario.sort(key=lambda x: (x.get("fecha", ""), x.get("hora", "")))

    print("Citas del usuario:", citas_usuario)
    return render_template("index.html", citas=citas_usuario)


# Página para agregar una nueva cita
@app.route("/nueva", methods=["GET", "POST"])
def nueva_cita():
    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":
        usuario = session["usuario"]
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")
        descripcion = request.form.get("descripcion")

        citas = cargar_json(CITAS_FILE)
        nueva = {
            "usuario": usuario,
            "fecha": fecha,
            "hora": hora,
            "descripcion": descripcion
        }
        citas.append(nueva)

        with open(CITAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)

        flash("Cita añadida con éxito", "success")
        return redirect("/")

    return render_template("nueva_cita.html")


# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Sesión cerrada", "success")
    return redirect("/login")


# Crear los archivos necesarios si no existen
def asegurar_archivos():
    for archivo in [USUARIOS_FILE, CITAS_FILE]:
        if not os.path.exists(archivo):
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
<<<<<<< HEAD
    app.run(debug=True)
=======
    app.run(debug=True)
>>>>>>> b3ff5f56529439b742ba18e7b42670995538008e
