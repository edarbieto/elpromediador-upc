from flask import Flask, render_template, request, jsonify
import sqlite3
import scraper
import datetime
import time

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


@app.route('/')
def index():
    data_visita = {}
    data_visita['FECHA_HORA'] = datetime.datetime.now()
    data_visita['IP'] = request.environ['HTTP_X_REAL_IP'].split(',')[0] if 'HTTP_X_REAL_IP' in request.environ else request.remote_addr
    add_visita = ("""
    INSERT INTO VISITA (FECHA_HORA, IP)
    VALUES (:FECHA_HORA, :IP)
    """)
    try:
        conn = sqlite3.connect('web.db')
        cur = conn.cursor()
        cur.execute(add_visita, data_visita)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/notas', methods=['POST'])
def notas():
    data_consulta = {}
    codigo = request.form.get('codigo')
    contrasena = request.form.get('contrasena')
    data_consulta['CODIGO_UPC'] = codigo
    data_consulta['FECHA_HORA_INICIO'] = datetime.datetime.now()
    consolidado = None
    try:
        consolidado = scraper.get_consolidado(codigo, contrasena)
        data_consulta['RESULTADO'] = 1
        data_consulta['NOMBRE'] = consolidado['nombre']
        data_consulta['CARRERA'] = consolidado['carrera']
        data_consulta['OBS'] = None
    except Exception as e:
        print(e)
        data_consulta['RESULTADO'] = 0
        data_consulta['NOMBRE'] = None
        data_consulta['CARRERA'] = None
        data_consulta['OBS'] = e
    data_consulta['FECHA_HORA_FIN'] = datetime.datetime.now()
    data_consulta['IP'] = request.environ['HTTP_X_REAL_IP'].split(',')[0] if 'HTTP_X_REAL_IP' in request.environ else request.remote_addr
    add_consulta = ("""
    INSERT INTO CONSULTA
    (CODIGO_UPC, FECHA_HORA_INICIO, FECHA_HORA_FIN, IP, RESULTADO, NOMBRE, CARRERA, OBS)
    VALUES (:CODIGO_UPC, :FECHA_HORA_INICIO, :FECHA_HORA_FIN, :IP, :RESULTADO, :NOMBRE, :CARRERA, :OBS)
    """)
    try:
        conn = sqlite3.connect('web.db')
        cur = conn.cursor()
        cur.execute(add_consulta, data_consulta)
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)
        return jsonify({'db_status': 'ERROR', 'consolidado': consolidado})
    return jsonify({'db_status': 'OK', 'consolidado': consolidado})


@app.route('/estadisticas', methods=['POST'])
def estadisticas():
    try:
        conn = sqlite3.connect('web.db')
        cur = conn.cursor()
        visitas = cur.execute('SELECT COUNT(1) FROM VISITA').fetchone()[0]
        consultas = cur.execute('SELECT COUNT(1) FROM CONSULTA').fetchone()[0]
        alumnos = cur.execute('SELECT COUNT(DISTINCT UPPER(CODIGO_UPC)) FROM CONSULTA WHERE RESULTADO = 1').fetchone()[0]
        tiempo_promedio = cur.execute("""
        SELECT CAST(ROUND(AVG(CAST((JULIANDAY(FECHA_HORA_FIN) - JULIANDAY(FECHA_HORA_INICIO)) * 24 * 60 * 60 AS INTEGER))) AS INTEGER)
        FROM CONSULTA
        WHERE RESULTADO = 1
        """).fetchone()[0]
        carreras = cur.execute("""
        SELECT CARRERA, COUNT(DISTINCT UPPER(CODIGO_UPC))
        FROM CONSULTA
        WHERE RESULTADO = 1
        GROUP BY CARRERA
        ORDER BY 2 DESC
        LIMIT 10
        """).fetchall()
        conn.commit()
        conn.close()
        return jsonify({
            'visitas': visitas,
            'consultas': consultas,
            'alumnos': alumnos,
            'tiempo_promedio': tiempo_promedio,
            'carreras': carreras
        })
    except Exception as e:
        print(e)
        return jsonify({'db_error': True})
