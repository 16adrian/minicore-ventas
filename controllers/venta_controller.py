from datetime import datetime

from flask import Blueprint, render_template, request

from models.regla import Regla
from models.vendedor import Vendedor
from models.venta import Venta

main_blueprint = Blueprint("main", __name__)


def convertir_fecha(texto):
    """Convierte '2025-06-01' en una fecha. Si viene vacio o mal, devuelve None."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@main_blueprint.route("/", methods=["GET", "POST"])
def resumen_comisiones():
    fecha_inicio = request.form.get("fecha_inicio", "")
    fecha_fin = request.form.get("fecha_fin", "")
    inicio = convertir_fecha(fecha_inicio)
    fin = convertir_fecha(fecha_fin)
    error = None

    if inicio and fin and fin < inicio:
        error = "La fecha de fin no puede ser menor que la fecha de inicio."
        inicio = fin = None

    # MODELO: pedimos los datos a la base de datos
    vendedores = Vendedor.query.order_by(Vendedor.id).all()
    reglas = Regla.query.order_by(Regla.monto_minimo.desc()).all()

    comisiones = []
    for vendedor in vendedores:
        consulta = Venta.query.filter(Venta.vendedor_id == vendedor.id)
        if inicio and fin:
            consulta = consulta.filter(Venta.fecha_venta >= inicio, Venta.fecha_venta <= fin)
        ventas = consulta.all()

        total = sum(v.cuota_monto for v in ventas)

        # Regla: la primera (de mayor a menor) cuyo monto minimo se alcance
        porcentaje = 0
        for regla in reglas:
            if total >= regla.monto_minimo:
                porcentaje = regla.porcentaje_comision
                break

        comisiones.append({
            "vendedor": vendedor.nombre,
            "num_ventas": len(ventas),
            "total_ventas": total,
            "porcentaje": porcentaje,
            "comision": total * porcentaje,
        })

    total_ventas = sum(c["total_ventas"] for c in comisiones)
    total_comisiones = sum(c["comision"] for c in comisiones)

    # VISTA: mandamos los resultados al HTML
    return render_template(
        "index.html",
        comisiones=comisiones,
        reglas=reglas,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        filtrado=bool(inicio and fin),
        error=error,
        total_ventas=total_ventas,
        total_comisiones=total_comisiones,
    )
