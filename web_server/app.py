from flask import Flask, render_template, request, jsonify
import scraper
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
    return render_template('index.html')


@app.route('/notas', methods=['POST'])
def notas():
    codigo = request.form.get('codigo')
    contrasena = request.form.get('contrasena')
    print(codigo, contrasena)
    # consolidado = scraper.get_consolidado(codigo, contrasena)
    consolidado = scraper.get_consolidado_dummy(codigo, contrasena)
    time.sleep(2)    
    print(consolidado['nombre'])
    return jsonify(consolidado)
