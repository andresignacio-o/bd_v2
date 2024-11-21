import psycopg2
import logging

def conectar_db():
    """Establece la conexión a la base de datos y retorna la conexión y el cursor."""
    try:
        conexion = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="liliput1521",
            port=5432
        )
        cursor = conexion.cursor()
        cursor.execute("SET search_path TO hito2;")
        print("Conexión exitosa a la base de datos.")
        return conexion, cursor
    except Exception as e:
        logging.error(f"Error al conectar a la base de datos: {e}")
        return None, None

def desconectar_db(conexion, cursor):
    """Cierra la conexión a la base de datos."""
    try:
        cursor.close()
        conexion.close()
        print("Desconexión exitosa de la base de datos.")
    except Exception as e:
        logging.error(f"Error al desconectar de la base de datos: {e}")
  