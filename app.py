from flask import Flask, render_template, request, redirect, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'TU_CLAVE_SECRETA_AQUI'  # Cambia esto por una clave segura y secreta

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
            if isinstance(data, list) and len(data) == 1 and isinstance(data[0], list):
                data = data[0]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# Crear los archivos necesarios si no existen
def asegurar_archivos():
    for archivo in [USUARIOS_FILE, CITAS_FILE]:
        if not os.path.exists(archivo):
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=4, ensure_ascii=False)


# Página de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
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
        cliente = request.form.get("cliente")
        tatuaje = request.form.get("tatuaje")
        precio = float(request.form.get("precio", 0))
        senal = float(request.form.get("senal", 0))
        comentarios = request.form.get("comentarios", "")

        citas = cargar_json(CITAS_FILE)
        nueva = {
            "usuario": usuario,
            "fecha": fecha,
            "hora": hora,
            "cliente": cliente,
            "tatuaje": tatuaje,
            "precio": precio,
            "senal": senal,
            "comentarios": comentarios
        }
        citas.append(nueva)

        with open(CITAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)

        flash("Cita añadida con éxito", "success")
        return redirect("/")

    return render_template("nueva_cita.html")


# Página para editar cita existente
@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    if "usuario" not in session:
        return redirect("/login")

    usuario = session["usuario"]
    citas = cargar_json(CITAS_FILE)
    citas_usuario = [c for c in citas if c.get("usuario") == usuario]

    if index < 0 or index >= len(citas_usuario):
        flash("Cita no encontrada", "danger")
        return redirect("/")

    cita = citas_usuario[index]

    if request.method == "POST":
        cita["fecha"] = request.form.get("fecha")
        cita["hora"] = request.form.get("hora")
        cita["cliente"] = request.form.get("cliente")
        cita["tatuaje"] = request.form.get("tatuaje")
        cita["precio"] = float(request.form.get("precio", 0))
        cita["senal"] = float(request.form.get("senal", 0))
        cita["comentarios"] = request.form.get("comentarios", "")

        # Actualizar cita en la lista global
        for i, c in enumerate(citas):
            if c == citas_usuario[index]:
                citas[i] = cita
                break

        with open(CITAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(citas, f, indent=4, ensure_ascii=False)

        flash("Cita actualizada", "success")
        return redirect("/")

    return render_template("editar_cita.html", cita=cita, index=index)


# Ruta para eliminar cita
@app.route("/eliminar/<int:index>", methods=["POST"])
def eliminar(index):
    if "usuario" not in session:
        return redirect("/login")

    usuario = session["usuario"]
    citas = cargar_json(CITAS_FILE)
    citas_usuario = [c for c in citas if c.get("usuario") == usuario]

    if index < 0 or index >= len(citas_usuario):
        flash("Cita no encontrada", "danger")
        return redirect("/")

    cita_a_eliminar = citas_usuario[index]
    citas = [c for c in citas if c != cita_a_eliminar]

    with open(CITAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(citas, f, indent=4, ensure_ascii=False)

    flash("Cita eliminada", "success")
    return redirect("/")


# Cerrar sesión
@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Sesión cerrada", "success")
    return redirect("/login")


if __name__ == "__main__":
    asegurar_archivos()
    app.run(debug=True)
