from flask import Flask, render_template, request, flash
from db import conectar_db, desconectar_db

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta'

# Lista de categorías definidas directamente
CATEGORIAS = ["Beverage", "Coffee", "Dishware", "Food", "Gum", "Kitchen", "Medicine"]

@app.route("/", methods=["GET", "POST"])
def home():
    """Página principal que maneja todas las consultas"""
    resultados_mas_vendidos = []
    resultados_patrones_compra = []
    resultados_bancos = []
    categoria = None
    fecha_inicio = None
    fecha_fin = None
    mes = None
    year_inicio = None
    year_fin = None
    year = None

    if request.method == "POST":
        consulta = request.form.get("consulta")

        if consulta == "productos_mas_vendidos":
            # Consulta 1: Productos más vendidos
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
                        resultados_mas_vendidos = cursor.fetchall()
                    except Exception as e:
                        flash(f"Error al ejecutar la consulta: {str(e)}", "error")
                        print("Error:", e)
                    finally:
                        desconectar_db(conexion, cursor)

        elif consulta == "patrones_compra":
            # Consulta 2: Patrones de compra
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
                        query = generar_consulta_dinamica(categoria, mes, year_inicio, year_fin)
                        cursor.execute(query, (categoria, mes, year_inicio, year_fin))
                        resultados_patrones_compra = cursor.fetchall()
                    except Exception as e:
                        flash("Error al ejecutar la consulta.", "error")
                        print("Error:", e)
                    finally:
                        desconectar_db(conexion, cursor)

        elif consulta == "banco_por_year":
            # Consulta 3: Ventas por bancos
            year = request.form.get("year")

            if not year or not year.isdigit():
                flash("Debe ingresar un año válido.", "error")
            else:
                conexion, cursor = conectar_db()
                if conexion and cursor:
                    try:
                        query = """
                        SELECT 
                            t.bank_name, 
                            TO_CHAR(SUM(f.total_price), 'FM999,999,999,999') AS total_ventas_formateado
                        FROM 
                            fact_table f
                        JOIN 
                            trans_dim t ON f.payment_key = t.payment_key
                        JOIN 
                            time_dim ti ON f.time_key = ti.time_key
                        WHERE 
                            ti.year = %s
                        GROUP BY 
                            t.bank_name
                        ORDER BY 
                            SUM(f.total_price) DESC;
                        """
                        cursor.execute(query, (year,))
                        resultados_bancos = cursor.fetchall()
                    except Exception as e:
                        flash("Error al ejecutar la consulta.", "error")
                        print("Error:", e)
                    finally:
                        desconectar_db(conexion, cursor)

    return render_template(
        "index.html",
        categorias=CATEGORIAS,
        resultados_mas_vendidos=resultados_mas_vendidos,
        resultados_patrones_compra=resultados_patrones_compra,
        resultados_bancos=resultados_bancos,
        categoria_seleccionada=categoria,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        mes=mes,
        year_inicio=year_inicio,
        year_fin=year_fin,
        year=year
    )

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


@app.route("/banco_por_year", methods=["GET", "POST"])
def banco_por_year():
    """Consulta ventas por bancos en un año específico."""
    resultados = []
    year = None

    if request.method == "POST":
        year = request.form.get("year")

        # Validamos que se haya proporcionado un año válido
        if not year or not year.isdigit():
            flash("Debe ingresar un año válido.", "error")
        else:
            # Conexión a la base de datos
            conexion, cursor = conectar_db()
            if conexion and cursor:
                try:
                    query = """
                    SELECT 
                        t.bank_name, 
                        TO_CHAR(SUM(f.total_price), 'FM999,999,999,999') AS total_ventas_formateado
                    FROM 
                        fact_table f
                    JOIN 
                        trans_dim t ON f.payment_key = t.payment_key
                    JOIN 
                        time_dim ti ON f.time_key = ti.time_key
                    WHERE 
                        ti.year = %s
                    GROUP BY 
                        t.bank_name
                    ORDER BY 
                        SUM(f.total_price) DESC;
                    """
                    cursor.execute(query, (year,))
                    resultados = cursor.fetchall()

                except Exception as e:
                    flash("Error al ejecutar la consulta.", "error")
                    print("Error:", e)
                finally:
                    # Cerramos la conexión
                    desconectar_db(conexion, cursor)

    return render_template("banco_por_year.html", resultados=resultados, year=year)

if __name__ == "__main__":
    app.run(debug=True)
