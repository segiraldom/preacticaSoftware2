from datetime import datetime

from extensions import db


class Cuenta(db.Model):
    __tablename__ = "cuentas"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), nullable=False, unique=True)
    numero_cuenta = db.Column(db.String(20), nullable=False, unique=True)
    saldo = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    estado = db.Column(db.String(20), nullable=False, default="activa")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "correo": self.correo,
            "numero_cuenta": self.numero_cuenta,
            "saldo": float(self.saldo),
            "estado": self.estado,
        }


class Movimiento(db.Model):
    __tablename__ = "movimientos"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cuenta_id = db.Column(db.Integer, db.ForeignKey("cuentas.id"), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    cuenta = db.relationship("Cuenta", backref=db.backref("movimientos", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "cuenta_id": self.cuenta_id,
            "tipo": self.tipo,
            "monto": float(self.monto),
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
        }
