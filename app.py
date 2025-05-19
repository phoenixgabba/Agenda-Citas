from flask import Flask, render_template, request, redirect, flash
import json
import os

app = Flask(__name__)
app.secret_key = "tu_clave_secreta"

CITAS_FILE = "citas.json"
CLIENTES_FILE = "clientes.json"

def asegurar_archivos():
    for file in [CITAS_FILE, CLIENTES_FILE]:
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

@app.route("/")
def index():
    asegurar_archivos()
    citas = cargar_json(CITAS_FILE)
    citas.sort(key=lambda x: (x["fecha"], x["hora"]))
    print("Citas cargadas:", citas)  # Debug
    return render_template("index.html", citas=citas)

@app.route("/nueva", methods=["GET", "POST"])
def nueva():
    asegurar_archivos()
    if request.method == "POST":
        nueva_cita = {
            "fecha": request.form.get("fecha"),
            "hora": request.form.get("hora"),
            "cliente": request.form.get("cliente"),
            "tatuaje": request.form.get("tatuaje"),
            "precio": to_float_safe(request.form.get("precio")),
            "senal": to_float_safe(request.form.get("senal")),
            "comentarios": request.form.get("comentarios", "").strip()
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
    asegurar_archivos()
    citas = cargar_json(CITAS_FILE)
    if index < 0 or index >= len(citas):
        flash("Cita no encontrada", "error")
        return redirect("/")

    cita = citas[index]

    if request.method == "POST":
        cita["fecha"] = request.form.get("fecha")
        cita["hora"] = request.form.get("hora")
        cita["cliente"] = request.form.get("cliente")
        cita["tatuaje"] = request.form.get("tatuaje")
        cita["precio"] = to_float_safe(request.form.get("precio"))
        cita["senal"] = to_float_safe(request.form.get("senal"))
        cita["comentarios"] = request.form.get("comentarios", "").strip()

        guardar_json(CITAS_FILE, citas)
        actualizar_cliente(cita["cliente"], cita["tatuaje"], cita["comentarios"])

        flash("Cita actualizada correctamente", "success")
        return redirect("/")

    return render_template("editar_cita.html", cita=cita, index=index)

@app.route("/eliminar/<int:index>", methods=["POST"])
def eliminar(index):
    asegurar_archivos()
    citas = cargar_json(CITAS_FILE)
    if 0 <= index < len(citas):
        eliminado = citas.pop(index)
        guardar_json(CITAS_FILE, citas)
        print("Cita eliminada:", eliminado)  # Debug
        flash(f"Cita de {eliminado['cliente']} eliminada correctamente", "success")
    else:
        flash("Índice de cita no válido", "error")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)