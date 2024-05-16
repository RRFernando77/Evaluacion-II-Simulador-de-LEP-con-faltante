from flask import Flask, request, jsonify, render_template
import random

app = Flask(__name__, static_folder="static")


def demanda_aleatoria(media, desviacion):
    """Genera una demanda aleatoria."""
    # Genera una demanda aleatoria utilizando una distribución normal con la media y desviación estándar dadas
    # Se asegura de que la demanda generada sea al menos cero
    return max(0, round(random.normalvariate(media, desviacion)))


def tiempo_entrega_aleatorio(media, desviacion):
    """Genera un tiempo de entrega aleatorio."""
    # Genera un tiempo de entrega aleatorio utilizando una distribución normal con la media y desviación estándar dadas
    # Se asegura de que el tiempo de entrega generado sea al menos uno para evitar división por cero
    return max(1, round(random.normalvariate(media, desviacion)))


def simulacion_LEP_con_faltante(
    demanda_media,
    desviacion_demanda,
    tiempo_entrega_media,
    desviacion_tiempo_entrega,
    costo_pedido,
    costo_faltante,
    costo_inventario,
    cantidad_inicial_inventario,
    tiempo_simulacion,
):
    """
    Realiza una simulación del Modelo de Lote Económico de Producción con faltante.

    Parámetros:
        demanda_media: Media de la demanda (unidades por período).
        desviacion_demanda: Desviación estándar de la demanda (unidades por período).
        tiempo_entrega_media: Media del tiempo de entrega (períodos).
        desviacion_tiempo_entrega: Desviación estándar del tiempo de entrega (períodos).
        costo_pedido: Costo de realizar un pedido (moneda por pedido).
        costo_faltante: Costo de faltante por unidad (moneda por unidad).
        costo_inventario: Costo de mantener una unidad en inventario por unidad de tiempo (moneda por unidad por período).
        cantidad_inicial_inventario: Cantidad inicial en inventario (unidades).
        tiempo_simulacion: Tiempo de simulación (períodos).

    Retorna:
        total_costo_pedido: Costo total de los pedidos realizados (moneda).
        total_costo_faltante: Costo total de faltante (moneda).
        total_costo_inventario: Costo total de mantener el inventario (moneda).
    """
    inventario = cantidad_inicial_inventario
    total_costo_pedido = 0
    total_costo_faltante = 0
    total_costo_inventario = 0
    info = []
    # Ciclo que simula el paso del tiempo
    for tiempo in range(tiempo_simulacion):
        # Genera una demanda y un tiempo de entrega aleatorios para el período actual
        demanda = demanda_aleatoria(demanda_media, desviacion_demanda)
        tiempo_entrega = tiempo_entrega_aleatorio(
            tiempo_entrega_media, desviacion_tiempo_entrega
        )

        # Verifica si hay faltante y actualiza los costos correspondientes
        if inventario < demanda:
            faltante = demanda - inventario
            inventario = 0
            total_costo_faltante += faltante * costo_faltante
            # Informa sobre el faltante y el estado del inventario

            info.append(
                f"Periodo {tiempo}: Se demandaron {demanda} unidades. Faltante de {faltante} unidades. Inventario: 0"
            )

        else:
            faltante = 0
            inventario -= demanda
            # Informa sobre la satisfacción de la demanda y el estado del inventario
            info.append(
                f"Periodo {tiempo}: Se demandaron {demanda} unidades. Demanda satisfecha. Inventario: {inventario}"
            )

        # Calcula el costo de mantener el inventario y actualiza el costo total de inventario
        costo_inventario_tiempo = inventario * costo_inventario
        total_costo_inventario += costo_inventario_tiempo

        # Verifica si es tiempo de realizar un pedido
        if tiempo_entrega != 0 and tiempo % tiempo_entrega == 0:
            # Realiza un pedido y actualiza el inventario
            total_costo_pedido += costo_pedido
            inventario += demanda
            # Informa sobre la realización del pedido y el estado del inventario
            info.append(
                f"Periodo {tiempo}: Se realizó un pedido de {demanda} unidades. Inventario: {inventario}"
            )

    # Devuelve los costos totales al final de la simulación
    return {
        "total_costo_pedido": total_costo_pedido,
        "total_costo_faltante": total_costo_faltante,
        "total_costo_inventario": total_costo_inventario,
        "info": info,
    }


@app.route("/")
def formulario():
    """
    Función para renderizar el formulario HTML.

    Retorna:
        str: Plantilla HTML del formulario.
    """
    return render_template("formulario.html")


@app.route("/simular_lep_con_faltante", methods=["POST"])
def simular_lep_con_faltante():
    """
    Función para simular el LEP con faltante utilizando los datos del formulario.

    Retorna:
        dict: Resultados de la simulación en formato JSON.
    """
    try:
        # Obtiene los datos del formulario
        data = request.json

        # Realiza la simulación del LEP con faltante
        resultados = simulacion_LEP_con_faltante(
            demanda_media=int(data["demanda_media"]),
            desviacion_demanda=float(data["desviacion_demanda"]),
            tiempo_entrega_media=int(data["tiempo_entrega_media"]),
            desviacion_tiempo_entrega=float(data["desviacion_tiempo_entrega"]),
            costo_pedido=float(data["costo_pedido"]),
            costo_faltante=float(data["costo_faltante"]),
            costo_inventario=float(data["costo_inventario"]),
            cantidad_inicial_inventario=int(data["cantidad_inicial_inventario"]),
            tiempo_simulacion=int(data["tiempo_simulacion"]),
        )
        resultados["estado"] = "exitoso"
        # Retorna los resultados de la simulación en formato JSON
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"estado": "error", "error": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
