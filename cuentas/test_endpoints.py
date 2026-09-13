"""Pruebas de integración para todos los endpoints de la API."""
import json
import sys
import uuid

from app import create_app
from extensions import db
from models import Cuenta, Movimiento


def run_tests():
    app = create_app()
    client = app.test_client()
    resultados = []
    cuenta_id = None
    sufijo = uuid.uuid4().hex[:8]

    def registrar(nombre, ok, detalle=""):
        estado = "PASS" if ok else "FAIL"
        resultados.append((nombre, estado, detalle))
        simbolo = "[OK]" if ok else "[FAIL]"
        print(f"  {simbolo} {nombre}" + (f" - {detalle}" if detalle else ""))

    print("\n=== PRUEBAS DE ENDPOINTS ===\n")

    # --- POST /accounts ---
    print("POST /accounts")
    resp = client.post(
        "/accounts",
        json={
            "nombre": "Sebastian",
            "apellido": "Test",
            "correo": f"sebastian.test.{sufijo}@mail.com",
        },
    )
    data = resp.get_json()
    registrar(
        "Crear cuenta (201)",
        resp.status_code == 201 and "cuenta" in data,
        f"status={resp.status_code}",
    )
    cuenta_id = data.get("cuenta", {}).get("id") if resp.status_code == 201 else None

    resp_dup = client.post(
        "/accounts",
        json={
            "nombre": "Otro",
            "apellido": "Usuario",
            "correo": f"sebastian.test.{sufijo}@mail.com",
        },
    )
    registrar(
        "Correo duplicado al crear (409)",
        resp_dup.status_code == 409,
        f"status={resp_dup.status_code}",
    )

    # --- GET /accounts ---
    print("\nGET /accounts")
    resp = client.get("/accounts")
    data = resp.get_json()
    registrar(
        "Listar cuentas (200)",
        resp.status_code == 200 and isinstance(data.get("response"), list),
        f"total={len(data.get('response', []))}",
    )

    # --- GET /accounts/{id} ---
    print("\nGET /accounts/{id}")
    resp = client.get(f"/accounts/{cuenta_id}")
    data = resp.get_json()
    registrar(
        "Obtener cuenta por id (200)",
        resp.status_code == 200 and data["response"]["id"] == cuenta_id,
        f"status={resp.status_code}",
    )

    resp = client.get("/accounts/999999")
    registrar("Cuenta inexistente (404)", resp.status_code == 404, f"status={resp.status_code}")

    # --- GET /cuentas/{id}/saldo ---
    print("\nGET /cuentas/{id}/saldo")
    resp = client.get(f"/cuentas/{cuenta_id}/saldo")
    data = resp.get_json()
    registrar(
        "Consultar saldo (200)",
        resp.status_code == 200 and data["response"]["saldo"] == 0,
        f"saldo={data.get('response', {}).get('saldo')}",
    )

    resp = client.get("/cuentas/999999/saldo")
    registrar("Saldo cuenta inexistente (404)", resp.status_code == 404)

    # --- GET /cuentas/{id}/movimientos ---
    print("\nGET /cuentas/{id}/movimientos")
    with app.app_context():
        movimiento = Movimiento(
            cuenta_id=cuenta_id,
            tipo="deposito",
            monto=150.50,
            descripcion="Deposito de prueba",
        )
        db.session.add(movimiento)
        db.session.commit()

    resp = client.get(f"/cuentas/{cuenta_id}/movimientos")
    data = resp.get_json()
    registrar(
        "Listar movimientos (200)",
        resp.status_code == 200 and len(data["response"]) >= 1,
        f"movimientos={len(data.get('response', []))}",
    )

    resp = client.get("/cuentas/999999/movimientos")
    registrar("Movimientos cuenta inexistente (404)", resp.status_code == 404)

    # --- PUT /cuentas/{id} ---
    print("\nPUT /cuentas/{id}")
    resp = client.put(
        f"/cuentas/{cuenta_id}",
        json={
            "nombre": "Sebastian",
            "apellido": "Actualizado",
            "correo": f"sebastian.test.{sufijo}@mail.com",
        },
    )
    data = resp.get_json()
    registrar(
        "Actualizar cuenta completa (200)",
        resp.status_code == 200 and data["cuenta"]["apellido"] == "Actualizado",
        f"status={resp.status_code}",
    )

    resp = client.put(f"/cuentas/{cuenta_id}", json={"nombre": "Solo nombre"})
    registrar(
        "PUT sin campos requeridos (400)",
        resp.status_code == 400,
        f"status={resp.status_code}",
    )

    with app.app_context():
        otra = Cuenta(
            nombre="Otra",
            apellido="Cuenta",
            correo=f"otro.{sufijo}@mail.com",
            numero_cuenta="9999999999",
            saldo=0,
        )
        db.session.add(otra)
        db.session.commit()
        otra_id = otra.id

    resp = client.put(
        f"/cuentas/{cuenta_id}",
        json={
            "nombre": "Sebastian",
            "apellido": "Actualizado",
            "correo": f"otro.{sufijo}@mail.com",
        },
    )
    registrar(
        "PUT correo duplicado (409)",
        resp.status_code == 409,
        f"status={resp.status_code}",
    )

    # --- PATCH /cuentas/{id} ---
    print("\nPATCH /cuentas/{id}")
    resp = client.patch(
        f"/cuentas/{cuenta_id}",
        json={"nombre": "SebastianPatch"},
    )
    data = resp.get_json()
    registrar(
        "Actualizar parcialmente (200)",
        resp.status_code == 200 and data["cuenta"]["nombre"] == "SebastianPatch",
        f"status={resp.status_code}",
    )

    resp = client.patch(f"/cuentas/{cuenta_id}", json={"campo_invalido": "x"})
    registrar(
        "PATCH sin campos válidos (400)",
        resp.status_code == 400,
        f"status={resp.status_code}",
    )

    # --- POST /cuentas/{id}/bloquear ---
    print("\nPOST /cuentas/{id}/bloquear")
    resp = client.post(f"/cuentas/{cuenta_id}/bloquear")
    data = resp.get_json()
    registrar(
        "Bloquear cuenta (200)",
        resp.status_code == 200 and data["cuenta"]["estado"] == "bloqueada",
        f"estado={data.get('cuenta', {}).get('estado')}",
    )

    resp = client.post(f"/cuentas/{cuenta_id}/bloquear")
    registrar(
        "Bloquear cuenta ya bloqueada (400)",
        resp.status_code == 400,
        f"status={resp.status_code}",
    )

    # --- POST /cuentas/{id}/activar ---
    print("\nPOST /cuentas/{id}/activar")
    resp = client.post(f"/cuentas/{cuenta_id}/activar")
    data = resp.get_json()
    registrar(
        "Activar cuenta (200)",
        resp.status_code == 200 and data["cuenta"]["estado"] == "activa",
        f"estado={data.get('cuenta', {}).get('estado')}",
    )

    resp = client.post(f"/cuentas/{cuenta_id}/activar")
    registrar(
        "Activar cuenta ya activa (400)",
        resp.status_code == 400,
        f"status={resp.status_code}",
    )

    # --- DELETE /cuentas/{id} ---
    print("\nDELETE /cuentas/{id}")
    with app.app_context():
        cuenta = Cuenta.query.get(cuenta_id)
        cuenta.saldo = 100
        db.session.commit()

    resp = client.delete(f"/cuentas/{cuenta_id}")
    registrar(
        "Eliminar con saldo distinto de cero (400)",
        resp.status_code == 400,
        f"status={resp.status_code}",
    )

    with app.app_context():
        cuenta = Cuenta.query.get(cuenta_id)
        cuenta.saldo = 0
        db.session.commit()

    resp = client.delete(f"/cuentas/{cuenta_id}")
    registrar(
        "Eliminar cuenta con saldo cero (200)",
        resp.status_code == 200,
        f"status={resp.status_code}",
    )

    resp = client.delete(f"/cuentas/{cuenta_id}")
    registrar(
        "Eliminar cuenta ya eliminada (404)",
        resp.status_code == 404,
        f"status={resp.status_code}",
    )

    # --- Limpieza ---
    with app.app_context():
        Movimiento.query.filter_by(cuenta_id=cuenta_id).delete()
        Cuenta.query.filter(Cuenta.id.in_([cuenta_id, otra_id])).delete(
            synchronize_session=False
        )
        db.session.commit()

    # --- Resumen ---
    total = len(resultados)
    pasaron = sum(1 for _, estado, _ in resultados if estado == "PASS")
    fallaron = total - pasaron

    print("\n=== RESUMEN ===")
    print(f"Total: {total} | Pasaron: {pasaron} | Fallaron: {fallaron}")

    if fallaron:
        print("\nPruebas fallidas:")
        for nombre, estado, detalle in resultados:
            if estado == "FAIL":
                print(f"  - {nombre}: {detalle}")

    return fallaron == 0


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
