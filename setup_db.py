# setup_db.py
import sqlite3
import os

# Ruta a la base de datos dentro del proyecto
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "productos.db")

# Conexión a la base de datos
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear la tabla productos
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    imagen TEXT
)
""")

# Datos de ejemplo para probar
productos_ejemplo = [
    ("Llavero Pikachu", "Llavero 3D impreso de Pikachu", 8.50, "pikachu.jpg"),
    ("Figura Goku", "Figura coleccionable Goku Super Saiyajin", 15.00, "goku.jpg"),
    ("Llaveros personalizados", "Llaveros con nombres o logos", 5.00, "personalizado.jpg")
]

# Insertar los productos si la tabla está vacía
cursor.execute("SELECT COUNT(*) FROM productos")
if cursor.fetchone()[0] == 0:
    cursor.executemany("""
    INSERT INTO productos (nombre, descripcion, precio, imagen)
    VALUES (?, ?, ?, ?)
    """, productos_ejemplo)
    print("Productos de ejemplo insertados.")
else:
    print("La tabla ya tiene datos, no se insertaron duplicados.")

# Guardar y cerrar
conn.commit()
conn.close()
print("Base de datos creada correctamente.")
