from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import smtplib
from email.message import EmailMessage
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

# Usuario fijo para login admin
USUARIO_ADMIN = "admin"
CLAVE_ADMIN = "1234"

# Carpeta donde se guardan las imágenes
UPLOAD_FOLDER = "static/IMG"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/productos")
def productos():
    categoria_filtrada = request.args.get("categoria")
    conexion = sqlite3.connect("data/productos.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT DISTINCT categoria FROM productos")
    categorias = [fila[0] for fila in cursor.fetchall() if fila[0]]

    if categoria_filtrada:
        cursor.execute("SELECT id, nombre, descripcion, precio, imagen, categoria FROM productos WHERE categoria = ?", (categoria_filtrada,))
    else:
        cursor.execute("SELECT id, nombre, descripcion, precio, imagen, categoria FROM productos")

    productos = [
        {
            "id": fila[0],
            "nombre": fila[1],
            "descripcion": fila[2],
            "precio": fila[3],
            "imagen": fila[4],
            "categoria": fila[5],
        }
        for fila in cursor.fetchall()
    ]

    conexion.close()
    return render_template("productos.html", productos=productos, categorias=categorias, categoria=categoria_filtrada)

@app.route("/carrito")
def carrito():
    return render_template("carrito.html")

@app.route("/contacto")
def contacto():
    return render_template("contact.html")

@app.route("/hacer-pedido", methods=["POST"])
def hacer_pedido():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]
    comentario = request.form.get("comentario", "")
    direccion = request.form.get("direccion", "")
    pedido_json = request.form["pedido"]
    envio = request.form.get("envio", "no")

    try:
        pedido = json.loads(pedido_json)
    except:
        pedido = []

    resumen_pedido = ""
    total = 0

    for item in pedido:
        nombre_producto = item.get("nombre")
        cantidad = int(item.get("cantidad", 1))
        precio = float(item.get("precio", 0))
        subtotal = cantidad * precio
        total += subtotal
        resumen_pedido += f"- {nombre_producto} x{cantidad} = ${subtotal:.2f}\n"

    if envio == "si":
        total += 6.00
        resumen_pedido += "\n+ Envío a domicilio: $6.00\n"

    resumen_pedido += f"\nTOTAL: ${total:.2f}"

    mensaje = f"""
🛒 NUEVO PEDIDO DE LA TIENDA MR STL

👤 Nombre: {nombre}
📱 Teléfono: {telefono}
✏️ Comentario: {comentario}
🏠 Dirección: {direccion if envio == "si" else 'No solicitó envío'}

📦 Detalle del pedido:
{resumen_pedido}
"""

    msg = EmailMessage()
    msg.set_content(mensaje)
    msg["Subject"] = "📬 Nuevo pedido desde Mr STL"
    msg["From"] = "ymaster675@gmail.com"
    msg["To"] = "mr.stl3d@gmail.com"

    try:
        with smtplib.SMTP_SSL("smtp-relay.brevo.com", 465) as smtp:
            smtp.login("921e1d001@smtp-brevo.com", "nPQmTOCKbxM0AURF")
            smtp.send_message(msg)
    except Exception as e:
        print("❌ Error al enviar correo:", e)
        return "Hubo un error al enviar el pedido. Intenta más tarde."

    return render_template("pedido_exito.html")

# ------------------- PANEL ADMIN -------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("username")
        clave = request.form.get("password")
        if usuario == USUARIO_ADMIN and clave == CLAVE_ADMIN:
            session["admin"] = True  # Activamos sesión admin
            return redirect(url_for("admin_panel"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")
    return render_template("login.html")

@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        categoria = request.form["categoria"]
        imagen = request.files["imagen"]

        if imagen:
            nombre_archivo = secure_filename(imagen.filename)
            ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo)
            imagen.save(ruta)
        else:
            nombre_archivo = ""

        conexion = sqlite3.connect("data/productos.db")
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO productos (nombre, descripcion, precio, imagen, categoria) VALUES (?, ?, ?, ?, ?)",
            (nombre, descripcion, precio, nombre_archivo, categoria),
        )
        conexion.commit()
        conexion.close()

    # Cargar productos existentes
    conexion = sqlite3.connect("data/productos.db")
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conexion.close()

    return render_template("admin_panel.html", productos=productos)

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("inicio"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    conexion = sqlite3.connect("data/productos.db")
    cursor = conexion.cursor()

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        categoria = request.form["categoria"]
        imagen = request.files["imagen"]

        if imagen and imagen.filename != "":
            nombre_archivo = secure_filename(imagen.filename)
            ruta = os.path.join(app.config["UPLOAD_FOLDER"], nombre_archivo)
            imagen.save(ruta)
            cursor.execute("""
                UPDATE productos 
                SET nombre = ?, descripcion = ?, precio = ?, categoria = ?, imagen = ? 
                WHERE id = ?
            """, (nombre, descripcion, precio, categoria, nombre_archivo, id))
        else:
            cursor.execute("""
                UPDATE productos 
                SET nombre = ?, descripcion = ?, precio = ?, categoria = ? 
                WHERE id = ?
            """, (nombre, descripcion, precio, categoria, id))

        conexion.commit()
        conexion.close()
        return redirect(url_for("admin_panel"))

    # GET: mostrar el formulario con datos actuales
    cursor.execute("SELECT * FROM productos WHERE id = ?", (id,))
    producto = cursor.fetchone()
    conexion.close()

    if producto:
        producto_dict = {
            "id": producto[0],
            "nombre": producto[1],
            "descripcion": producto[2],
            "precio": producto[3],
            "imagen": producto[4],
            "categoria": producto[5],
        }
        return render_template("editar_producto.html", producto=producto_dict)
    else:
        return "Producto no encontrado", 404
    


@app.route("/eliminar_producto/<int:id>", methods=["POST"])
def eliminar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("login"))

    conexion = sqlite3.connect("data/productos.db")
    cursor = conexion.cursor()

    # Obtener nombre de la imagen para eliminarla también
    cursor.execute("SELECT imagen FROM productos WHERE id = ?", (id,))
    resultado = cursor.fetchone()
    if resultado and resultado[0]:
        ruta_imagen = os.path.join(app.config["UPLOAD_FOLDER"], resultado[0])
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)

    # Eliminar producto
    cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()

    return redirect(url_for("admin_panel"))

# ---------------------------------------------------

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
