from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import mysql.connector
import scraper
import datetime
import time
import os

load_dotenv()

app = Flask(__name__)

m_jinja_options = app.jinja_options.copy()
m_jinja_options.update(dict(
    block_start_string='<%',
    block_end_string='%>',
    variable_start_string='%%',
    variable_end_string='%%',
    comment_start_string='<#',
    comment_end_string='#>',
))
app.jinja_options = m_jinja_options

db_config = {
    'database': os.getenv('MYSQL_DB'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASS'),
    'host': os.getenv('MYSQL_HOST')
}

print(db_config)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/notas', methods=['POST'])
def notas():
    data_consulta = {}
    codigo = request.form.get('codigo')
    contrasena = request.form.get('contrasena')
    data_consulta['CODIGO_UPC'] = codigo
    data_consulta['FECHA_HORA_INICIO'] = datetime.datetime.now()
    consolidado = None
    try:
        consolidado = scraper.get_consolidado_dummy(codigo, contrasena)
        data_consulta['RESULTADO'] = 1
        data_consulta['NOMBRE'] = consolidado['nombre']
        data_consulta['CARRERA'] = consolidado['carrera']
        data_consulta['OBS'] = None
    except Exception as e:
        data_consulta['RESULTADO'] = 0
        data_consulta['NOMBRE'] = None
        data_consulta['CARRERA'] = None
        data_consulta['OBS'] = e
    data_consulta['FECHA_HORA_FIN'] = datetime.datetime.now()
    data_consulta['IP'] = request.remote_addr
    add_consulta = ("""
    INSERT INTO CONSULTA
    (CODIGO_UPC, FECHA_HORA_INICIO, FECHA_HORA_FIN, IP, RESULTADO, NOMBRE, CARRERA, OBS)
    VALUES (%(CODIGO_UPC)s, %(FECHA_HORA_INICIO)s, %(FECHA_HORA_FIN)s, %(IP)s, %(RESULTADO)s, %(NOMBRE)s, %(CARRERA)s, %(OBS)s)
    """)
    error_db = None
    try:
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute(add_consulta, data_consulta)
        conn.commit()
        cur.close()
        conn.close()
    except:
        return jsonify({'db_status': 'ERROR', 'consolidado': consolidado})
    return jsonify({'db_status': 'OK', 'consolidado': consolidado})
