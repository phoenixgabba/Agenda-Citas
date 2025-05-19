from flask import Flask, render_template, request, redirect, flash, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"

CITAS_FILE = "citas.json"
CLIENTES_FILE = "clientes.json"
USUARIOS_FILE = "usuarios.json"

def asegurar_archivos():
    for file in [CITAS_FILE, CLIENTES_FILE, USUARIOS_FILE]:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                f.write("[]")

def cargar_json(file):
    with open(file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def guardar_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def to_float_safe(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def actualizar_cliente(nombre_cliente, tatuaje, comentario):
    clientes = cargar_json(CLIENTES_FILE)
    cliente = next((c for c in clientes if c["nombre"].lower() == nombre_cliente.lower()), None)

    if cliente:
        if tatuaje and tatuaje not in cliente["tatuajes"]:
            cliente["tatuajes"].append(tatuaje)
        if comentario:
            cliente["comentarios"].append(comentario)
    else:
        cliente = {
            "nombre": nombre_cliente,
            "tatuajes": [tatuaje] if tatuaje else [],
            "comentarios": [comentario] if comentario else []
        }
        clientes.append(cliente)

    guardar_json(CLIENTES_FILE, clientes)

def usuario_actual():
    return session.get("usuario")

def login_requerido():
    if "usuario" not in session:
        flash("Debes iniciar sesión para acceder", "warning")
        return redirect(url_for("login"))

@app.route("/")
def index():
    asegurar_archivos()
    if "usuario" not in session:
        return redirect("/login")
    citas = cargar_json(CITAS_FILE)
    usuario = session["usuario"]
    citas_usuario = [c for c in citas if c.get("usuario") == usuario]
    citas_usuario.sort(key=lambda x: (x["fecha"], x["hora"]))
    return render_template("index.html", citas=citas_usuario)

@app.route("/nueva", methods=["GET", "POST"])
def nueva():
    if not usuario_actual():
        return redirect("/login")
    asegurar_archivos()
    if request.method == "POST":
        nueva_cita = {
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "cliente": request.form.get("cliente"),
            "tatuaje": request.form.get("tatuaje"),
            "precio": to_float_safe(request.form.get("precio")),
            "senal": to_float_safe(request.form.get("senal")),
            "comentarios": request.form.get("comentarios", "").strip(),
            "usuario": usuario_actual()
        }

        citas = cargar_json(CITAS_FILE)
        citas.append(nueva_cita)
        guardar_json(CITAS_FILE, citas)

        actualizar_cliente(nueva_cita["cliente"], nueva_cita["tatuaje"], nueva_cita["comentarios"])

        flash("Cita añadida correctamente", "success")
        return redirect("/")
    return render_template("nueva_cita.html")

@app.route("/editar/<int:index>", methods=["GET", "POST"])
def editar(index):
    if not usuario_actual():
        return redirect("/login")
    asegurar_archivos()
    citas = cargar_json(CITAS_FILE)
    citas_usuario = [c for c in citas if c.get("usuario") == usuario_actual()]

    if index < 0 or index >= len(citas_usuario):
        flash("Cita no encontrada", "error")
        return redirect("/")

    cita = citas_usuario[index]
    cita_global_index = citas.index(cita)

    if request.method == "POST":
        cita["fecha"] = request.form.get("fecha")
        cita["hora"] = request.form.get("hora")
        cita["cliente"] = request.form.get("cliente")
        cita["tatuaje"] = request.form.get("tatuaje")
        cita["precio"] = to_float_safe(request.form.get("precio"))
        cita["senal"] = to_float_safe(request.form.get("senal"))
        cita["comentarios"] = request.form.get("comentarios", "").strip()

        citas[cita_global_index] = cita
        guardar_json(CITAS_FILE, citas)
        actualizar_cliente(cita["cliente"], cita["tatuaje"], cita["comentarios"])

        flash("Cita actualizada correctamente", "success")
        return redirect("/")

    return render_template("editar_cita.html", cita=cita, index=index)

@app.route("/eliminar/<int:index>", methods=["POST"])
def eliminar(index):
    if not usuario_actual():
        return redirect("/login")
    asegurar_archivos()
    citas = cargar_json(CITAS_FILE)
    citas_usuario = [c for c in citas if c.get("usuario") == usuario_actual()]

    if 0 <= index < len(citas_usuario):
        cita = citas_usuario[index]
        citas.remove(cita)
        guardar_json(CITAS_FILE, citas)
        flash(f"Cita de {cita['cliente']} eliminada correctamente", "success")
    else:
        flash("Índice de cita no válido", "error")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    asegurar_archivos()
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        if not usuario or not password:
            flash("Completa todos los campos", "error")
            return redirect("/register")

        usuarios = cargar_json(USUARIOS_FILE)
        if any(u["usuario"] == usuario for u in usuarios):
            flash("El usuario ya existe", "error")
            return redirect("/register")

        usuarios.append({"usuario": usuario, "password": password})
        guardar_json(USUARIOS_FILE, usuarios)
        flash("Registro exitoso, ahora inicia sesión", "success")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    asegurar_archivos()
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")

        usuarios = cargar_json(USUARIOS_FILE)
        user = next((u for u in usuarios if u["usuario"] == usuario and u["password"] == password), None)

        if user:
            session["usuario"] = usuario
            flash("Sesión iniciada", "success")
            return redirect("/")
        else:
            flash("Credenciales inválidas", "error")
            return redirect("/login")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Sesión cerrada", "info")
    return redirect("/login")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


