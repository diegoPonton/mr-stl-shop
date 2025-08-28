import sqlite3

# Conectar (si no existe, se crea)
conn = sqlite3.connect('productos.db')
cursor = conn.cursor()

# Crear tabla productos
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio REAL NOT NULL,
    imagen TEXT
)
""")

# Puedes insertar datos de prueba opcionalmente:
cursor.execute("""
INSERT INTO productos (nombre, descripcion, precio, imagen)
VALUES 
('Llavero Pikachu', 'Llavero impreso en 3D de Pikachu', 5.99, 'img/producto1.jpeg'),
('Figura Goku', 'Figura coleccionable de Goku Super Saiyan', 14.99, 'img/producto2.jpeg')
""")

# Guardar y cerrar
conn.commit()
conn.close()

print("✅ Base de datos y tabla creadas con éxito.")
