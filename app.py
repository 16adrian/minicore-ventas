import os
import sqlite3

from flask import Flask

from utils.database import db

# Carpeta donde vive este archivo (asi la ruta funciona en tu PC y en Render)
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_BD = os.path.join(CARPETA, "db.sqlite3")
RUTA_SQL = os.path.join(CARPETA, "data.sql")


def crear_base_de_datos():
    """Crea las tablas y carga los datos de ejemplo usando data.sql."""
    with sqlite3.connect(RUTA_BD) as conexion:
        with open(RUTA_SQL, encoding="utf-8") as archivo:
            conexion.executescript(archivo.read())


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + RUTA_BD
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-de-desarrollo")

crear_base_de_datos()
db.init_app(app)

from controllers.venta_controller import main_blueprint  # noqa: E402

app.register_blueprint(main_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
