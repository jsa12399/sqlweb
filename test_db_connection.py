# test_db_connection.py

import pyodbc

# Cadena de conexión usando autenticación de Windows (Trusted_Connection)
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\SQLEXPRESS;"  # Asegúrate de que este es tu servidor/instancia
    "DATABASE=WEBFIT_DB;"    # Asegúrate de que este es el nombre de tu base de datos
    "Trusted_Connection=yes;"
)

try:
    cnxn = pyodbc.connect(conn_str)
    cursor = cnxn.cursor()
    cursor.execute("SELECT GETDATE()") # Una consulta simple para verificar
    row = cursor.fetchone()
    print("--------------------------------------------------")
    print("             RESULTADO DE CONEXIÓN A BD           ")
    print("--------------------------------------------------")
    print("Conexión exitosa. Fecha actual del servidor:", row[0])
    print("--------------------------------------------------")
    cursor.close()
    cnxn.close()
except pyodbc.Error as ex:
    sqlstate = ex.args[0]
    print("--------------------------------------------------")
    print("         ERROR AL CONECTAR CON LA BASE DE DATOS   ")
    print("--------------------------------------------------")
    print(f"Error al conectar con SQL Server: {sqlstate}")
    print(f"Detalles del error: {ex}")
    print("--------------------------------------------------")

print("\nVerificación de conexión finalizada.")