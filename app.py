from flask import Flask, render_template, request, flash
from db import conectar_db, desconectar_db

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta'  # Cambia esto a algo seguro para usar mensajes flash

# Lista de categorías definidas directamente
CATEGORIAS = ["Beverage", "Coffee", "Dishware", "Food", "Gum", "Kitchen", "Medicine"]

@app.route("/")
def home():
    """Página inicial con botones para cada consulta."""
    return render_template("index.html")

# Consulta Productos Más Vendidos
@app.route("/mas_vendidos", methods=["GET", "POST"])
def mas_vendidos():
    categorias = CATEGORIAS
    resultados = []
    categoria = None
    fecha_inicio = None
    fecha_fin = None

    if request.method == "POST":
        categoria = request.form.get("categoria")
        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")

        if not categoria or not fecha_inicio or not fecha_fin:
            flash("Debe ingresar categoría y fechas válidas.", "error")
        else:
            conexion, cursor = conectar_db()
            if conexion and cursor:
                try:
                    query = """
                    SELECT i.item_key, i.item_name, SUM(f.quantity) AS cantidad_vendida
                    FROM fact_table f
                    JOIN item_dim i ON f.item_key = i.item_key
                    JOIN time_dim t ON f.time_key = t.time_key
                    WHERE i."desc" LIKE %s || '%%'
                    AND TO_TIMESTAMP(t.date, 'DD-MM-YYYY HH24:MI') BETWEEN %s AND %s
                    GROUP BY i.item_key, i.item_name
                    ORDER BY cantidad_vendida DESC;
                    """
                    cursor.execute(query, (categoria, fecha_inicio, fecha_fin))
                    resultados = cursor.fetchall()
                except Exception as e:
                    flash("Error al ejecutar la consulta.", "error")
                    print("Error:", e)
                finally:
                    desconectar_db(conexion, cursor)

    return render_template("mas_vendido.html", categorias=categorias, resultados=resultados)


def generar_consulta_dinamica(categoria, mes, year_inicio, year_fin):
    # Generar columnas dinámicas para cada año en el rango
    columnas = ", ".join(
        [f"SUM(CASE WHEN t.year = {year} THEN f.quantity ELSE 0 END) AS cantidad_{year}"
         for year in range(year_inicio, year_fin + 1)]
    )

    # Crear la consulta SQL
    query = f"""
    SELECT 
        i.item_key AS item_id, 
        i.item_name, 
        {columnas}
    FROM fact_table f
    JOIN item_dim i ON f.item_key = i.item_key
    JOIN time_dim t ON f.time_key = t.time_key
    WHERE i."desc" LIKE %s || '%%'
      AND CAST(t.month AS INT) = %s
      AND t.year BETWEEN %s AND %s
    GROUP BY i.item_key, i.item_name
    ORDER BY i.item_name;
    """
    return query


# Consulta Patrones de Compra
@app.route("/patrones_compra", methods=["GET", "POST"])
def patrones_compra():
    resultados = []
    categoria = None
    mes = None
    year_inicio = None
    year_fin = None

    if request.method == "POST":
        categoria = request.form.get("categoria")
        mes = request.form.get("mes")
        year_inicio = int(request.form.get("year_inicio"))
        year_fin = int(request.form.get("year_fin"))

        if not categoria or not mes or not year_inicio or not year_fin:
            flash("Debe ingresar todos los datos válidos.", "error")
        else:
            conexion, cursor = conectar_db()
            if conexion and cursor:
                try:
                    # Generar la consulta dinámica
                    query = generar_consulta_dinamica(categoria, mes, year_inicio, year_fin)

                    # Ejecutar la consulta
                    cursor.execute(query, (categoria, mes, year_inicio, year_fin))
                    resultados = cursor.fetchall()
                except Exception as e:
                    flash("Error al ejecutar la consulta.", "error")
                    print("Error:", e)
                finally:
                    desconectar_db(conexion, cursor)

    return render_template(
        "patrones_compra.html",
        resultados=resultados,
        categorias=CATEGORIAS,
        categoria=categoria,
        mes=mes,
        year_inicio=year_inicio,
        year_fin=year_fin
    )


# Otra Consulta (Pendiente de Implementación)
@app.route("/otra_consulta", methods=["GET", "POST"])
def otra_consulta():
    """Ruta para una tercera consulta."""
    # Lógica para la consulta futura
    return render_template("otra_consulta.html")

if __name__ == "__main__":
    app.run(debug=True)
