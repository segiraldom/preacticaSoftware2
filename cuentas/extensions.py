"""Extensiones compartidas de la aplicación.

Se define aquí una única instancia de SQLAlchemy para que sea
inicializada una sola vez (con db.init_app(app)) y compartida por
toda la aplicación, evitando crear conexiones/engines duplicados.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
