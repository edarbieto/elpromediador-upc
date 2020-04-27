from flask import Flask, render_template, request
import scraper

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/notas', methods=['POST'])
def notas():
    codigo = request.form.get('codigo')
    contrasena = request.form.get('contrasena')
    consolidado = scraper.get_consolidado(codigo, contrasena)
    return render_template('notas.html', consolidado=consolidado)
