import json
import os
from flask import Blueprint, render_template, request

test_bp = Blueprint("test_bp", __name__, url_prefix="/test")

# Función simulada de cálculo de ruta, reemplaza por tu lógica real


def calculate_ride(data):
    # Aquí debes poner tu función real que calcule la ruta con los datos recibidos.
    # Por ahora, devuelve un ejemplo simple.
    return {"result": "Cálculo de ruta simulado", "input": data}


@test_bp.route("/")
def run_tests():
    test_files = {
        'Servicio corto (SIN PARADA)': 'tests/short_ride_no_stop.json',
        'Servicio corto (CON PARADA)': 'tests/short_ride_with_stop.json',
        'Servicio Corto (Aeropuerto)(SIN PARADA)': 'tests/near_airport_no_stop.json',
        'Servicio Corto (Aeropuerto) (CON PARADA)': 'tests/near_airport_with_stop.json',
        'Servicio largo (SIN PARADA)': 'tests/long_ride_no_stop.json',
        'Servicio largo (CON PARADA)': 'tests/long_ride_with_stop.json',
        'Servicio largo (Aeropuerto) (SIN PARADA)': 'tests/long_ride_no_stop_airport.json',
        'Servicio largo (Aeropuerto) (CON PARADA)': 'tests/long_ride_with_stop_airport.json',
    }

    output = []

    for title, filepath in test_files.items():
        # Ajusta ruta si es necesario
        full_path = os.path.join("public", "storage", filepath)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                test_data = json.load(f)
        except Exception as e:
            output.append({
                "title": title,
                "error": f"No se pudo cargar archivo {filepath}: {str(e)}"
            })
            continue

        # Llama a la función que procesa la ruta con el json cargado
        result = calculate_ride(test_data)

        output.append({
            "title": title,
            "input": test_data,
            "result": result,
        })

    return render_template("test_results.html", output=output)
