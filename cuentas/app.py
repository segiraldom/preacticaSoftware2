import random

from flask import Flask, request, jsonify

from conexion_bd import Config
from extensions import db
from models import Cuenta, Movimiento


def create_app():
    """Application factory: crea y configura la app Flask.

    La conexión a la base de datos se inicializa una única vez aquí
    (db.init_app(app)) y SQLAlchemy administra internamente un pool
    de conexiones que se reutiliza en todas las peticiones, evitando
    abrir y cerrar una conexión nueva en cada request.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    registrar_rutas(app)
    return app


def generar_numero_cuenta():
    """Genera un número de cuenta aleatorio único de 10 dígitos."""
    while True:
        numero = "".join(random.choices("0123456789", k=10))
        existe = Cuenta.query.filter_by(numero_cuenta=numero).first()
        if not existe:
            return numero


def obtener_cuenta_o_404(id):
    cuenta = Cuenta.query.get(id)
    if cuenta is None:
        return None, (jsonify({"response": "Cuenta no encontrada"}), 404)
    return cuenta, None


def correo_en_uso(correo, excluir_id=None):
    query = Cuenta.query.filter_by(correo=correo)
    if excluir_id is not None:
        query = query.filter(Cuenta.id != excluir_id)
    return query.first() is not None


def registrar_rutas(app):
    @app.route("/accounts", methods=["POST"])
    def save():
        data = request.json

        if correo_en_uso(data["correo"]):
            return jsonify({"response": "El correo ya está registrado"}), 409

        cuenta = Cuenta(
            nombre=data["nombre"],
            apellido=data["apellido"],
            correo=data["correo"],
            numero_cuenta=generar_numero_cuenta(),
            saldo=0,
        )
        db.session.add(cuenta)
        db.session.commit()

        return jsonify({
            "response": "Se ha creado correctamente",
            "cuenta": cuenta.to_dict(),
        }), 201

    @app.route("/accounts", methods=["GET"])
    def get_accounts():
        cuentas = Cuenta.query.all()
        return jsonify({
            "response": [cuenta.to_dict() for cuenta in cuentas]
        })

    @app.route("/accounts/<int:id>", methods=["GET"])
    def get_account(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        return jsonify({
            "response": cuenta.to_dict()
        })

    @app.route("/accounts/<int:id>", methods=["PUT"])
    def actualizar_cuenta(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        data = request.json or {}
        campos_requeridos = ("nombre", "apellido", "correo")
        faltantes = [campo for campo in campos_requeridos if campo not in data]
        if faltantes:
            return jsonify({
                "response": f"Campos requeridos faltantes: {', '.join(faltantes)}"
            }), 400

        if correo_en_uso(data["correo"], excluir_id=id):
            return jsonify({"response": "El correo ya está registrado"}), 409

        cuenta.nombre = data["nombre"]
        cuenta.apellido = data["apellido"]
        cuenta.correo = data["correo"]
        db.session.commit()

        return jsonify({
            "response": "Cuenta actualizada correctamente",
            "cuenta": cuenta.to_dict(),
        })

    @app.route("/accounts/<int:id>", methods=["PATCH"])
    def actualizar_cuenta_parcial(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        data = request.json or {}
        campos_permitidos = ("nombre", "apellido", "correo")
        campos_a_actualizar = {k: v for k, v in data.items() if k in campos_permitidos}

        if not campos_a_actualizar:
            return jsonify({
                "response": "No se proporcionaron campos válidos para actualizar"
            }), 400

        if "correo" in campos_a_actualizar and correo_en_uso(
            campos_a_actualizar["correo"], excluir_id=id
        ):
            return jsonify({"response": "El correo ya está registrado"}), 409

        for campo, valor in campos_a_actualizar.items():
            setattr(cuenta, campo, valor)

        db.session.commit()

        return jsonify({
            "response": "Cuenta actualizada parcialmente",
            "cuenta": cuenta.to_dict(),
        })

    @app.route("/accounts/<int:id>", methods=["DELETE"])
    def eliminar_cuenta(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        if float(cuenta.saldo) != 0:
            return jsonify({
                "response": "No se puede eliminar una cuenta con saldo distinto de cero"
            }), 400

        Movimiento.query.filter_by(cuenta_id=id).delete()
        db.session.delete(cuenta)
        db.session.commit()

        return jsonify({"response": "Cuenta eliminada correctamente"})

    @app.route("/accounts/<int:id>/saldo", methods=["GET"])
    def obtener_saldo(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        return jsonify({
            "response": {
                "id": cuenta.id,
                "numero_cuenta": cuenta.numero_cuenta,
                "saldo": float(cuenta.saldo),
            }
        })

    @app.route("/accounts/<int:id>/movimientos", methods=["GET"])
    def obtener_movimientos(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        movimientos = (
            Movimiento.query.filter_by(cuenta_id=id)
            .order_by(Movimiento.fecha.desc())
            .all()
        )

        return jsonify({
            "response": [movimiento.to_dict() for movimiento in movimientos]
        })

    @app.route("/accounts/<int:id>/bloquear", methods=["POST"])
    def bloquear_cuenta(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        if cuenta.estado == "bloqueada":
            return jsonify({"response": "La cuenta ya está bloqueada"}), 400

        cuenta.estado = "bloqueada"
        db.session.commit()

        return jsonify({
            "response": "Cuenta bloqueada correctamente",
            "cuenta": cuenta.to_dict(),
        })

    @app.route("/accounts/<int:id>/activar", methods=["POST"])
    def activar_cuenta(id):
        cuenta, error = obtener_cuenta_o_404(id)
        if error:
            return error

        if cuenta.estado == "activa":
            return jsonify({"response": "La cuenta ya está activa"}), 400

        cuenta.estado = "activa"
        db.session.commit()

        return jsonify({
            "response": "Cuenta activada correctamente",
            "cuenta": cuenta.to_dict(),
        })
    
    @app.route("/example", methods=["POST"])
    def example():
        datos = request.json
        valor = datos["dato"]
        return jsonify({
            "response": valor
        })


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
