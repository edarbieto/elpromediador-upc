import requests
import scraper.cfscrape as cfscrape
import math
import json
from bs4 import BeautifulSoup

URL_UPC_INTRANET = 'https://intranet.upc.edu.pe'
URL_UPC_INTRANET_LOGIN = 'https://intranet.upc.edu.pe/LoginIntranet/loginUPC.aspx'
URL_UPC_INTRANET_NOTAS_PORTAL = 'https://intranet.upc.edu.pe/Programas/SesionnetNotas.asp?WPAG1=https://matricula.upc.edu.pe/ConsultaNotas/Resultado/Inicio'
URL_UPC_INTRANET_NOTAS_RESULTADO = 'https://matricula.upc.edu.pe/ConsultaNotas/Resultado/Inicio'
URL_UPC_INTRANET_NOTAS_INTERMEDIARIO = 'https://matricula.upc.edu.pe/ConsultaNotas/Intermediaria/Inicio'
URL_UPC_INTRANET_NOTAS_PERIODO = 'https://matricula.upc.edu.pe/ConsultaNotas/Curso/Inicio'


def get_consolidado(codigo, contrasena):
    # region Login UPC
    # Sesion
    session = cfscrape.create_scraper(delay=10)
    # Pasar CF Challengue
    session.get(URL_UPC_INTRANET)
    # Obtener cookies de sesion UPC
    session.get(URL_UPC_INTRANET_LOGIN)
    payload = {
        # Valores fijos
        'ctl00$ContentPlaceHolder1$Login1$LoginButton': 'Log+In',
        '__VIEWSTATE': '/wEPDwULLTEyNDExODE4MDIPZBYCZg9kFgICAw9kFgQCAQ9kFgRmD2QWAmYPZBYEAgEPDxYCHgRUZXh0BRJJbmdyZXNvIGEgSW50cmFuZXRkZAILDw9kFgIeDGF1dG9jb21wbGV0ZQUDb2ZmZAIBDw8WAh8AZWRkAgUPFgIeB1Zpc2libGVoZGS0FthQyIyRSzNqvOeGTXVAcTtx1Q==',
        '__EVENTVALIDATION': '/wEWCgK4uvTRCgK/1YTzDQLu8I/0DgLM97qYBQLSg7TsDQLlnevtBgKvzYqzCwLNtOGYDQKNrajcBALItoaIC457Do+w+vXwcocF8e2+XVp8tPKW',
        # Credenciales
        'ctl00$ContentPlaceHolder1$Login1$UserName': codigo,
        'ctl00$ContentPlaceHolder1$Login1$Password': contrasena
    }
    # Loggeo a UPC
    session.post(URL_UPC_INTRANET_LOGIN, data=payload)
    # Obtener credenciales encriptadas UPC
    html = session.get(URL_UPC_INTRANET_NOTAS_PORTAL)
    soup = BeautifulSoup(html.content, features='html.parser')
    payload = {x['id']: x['value'] for x in soup.findAll('input')}
    # Ingresar a modulo notas
    session.post(URL_UPC_INTRANET_NOTAS_RESULTADO, data=payload)
    # endregion
    # region Scrapping notas
    # Obtener data general
    html = session.get(URL_UPC_INTRANET_NOTAS_INTERMEDIARIO)
    soup = BeautifulSoup(html.text, features='html.parser')
    # Construir consolidado
    consolidado = {}
    consolidado['codigo'] = codigo.lower()
    consolidado['nombre'] = soup.find('span', {'id': 'spnAlumno_MatriculaActual1'}).text.replace('\n', '').strip().split('-')[1].strip()
    consolidado['carrera'] = soup.find('span', {'id': 'spnTipoIngreso'}).text.replace(':', '').replace('\n', '').strip()
    consolidado['ciclo_actual'] = int(soup.find('span', {'id': 'spnCiclo'}).text.replace(':', '').replace('\n', '').strip())
    consolidado['ciclos'] = []
    creditos_cuenta_total = 0
    # Iterar a partir del anio de inicio hasta el anio actual
    anio_ingreso = int(codigo[1:5])
    anio_actual = consolidado['ciclo_actual'] // 100
    for anio in range(anio_ingreso, anio_actual + 1):
        for mes in range(3):
            periodo = anio * 100 + mes
            # Obtener notas por por periodo
            html = session.post(URL_UPC_INTRANET_NOTAS_PERIODO, data={'CodPeriodo': periodo})
            soup = BeautifulSoup(html.text, features='html.parser')
            # Validar que se matriculo en el ciclo
            if not soup.find('span', {'id': 'spnCiclo'}):
                continue
            # cursos_count = int(soup.find('span', {'id': 'spnNumAsignaturas'}).text.replace(' ', '').replace('\n', '').strip().replace(':', ''))
            soup_cursos = soup.findAll('table', {'width': '100%'})
            cursos_count = len(soup_cursos)
            # Validar scrapping anterior que sea correcto (numero de cursos)
            # if cursos_count != len(soup_cursos):
                # raise Exception('El numero de cursos no coincide con el HTML')
            # Construir ciclo
            ciclo = {}
            ciclo['id'] = int(periodo)
            ciclo['nivel'] = int(soup.find('span', {'id': 'spnNivel'}).text.replace(' ', '').replace('\n', '').replace(':', '').strip())
            ciclo['total_cursos'] = int(soup.find('span', {'id': 'spnNumAsignaturas'}).text.replace(' ', '').replace('\n', '').replace(':', '').strip())
            ciclo['total_creditos'] = int(soup.find('span', {'id': 'spnTotalCreditos'}).text.replace(' ', '').replace('\n', '').replace(':', '').strip())
            creditos_cuenta_total += ciclo['total_creditos']
            ciclo['estado'] = 'RETIRADO'
            ciclo['cursos'] = []
            # Iterar por cada curso
            for soup_curso in soup_cursos:
                # Construir curso
                curso = {}
                curso['codigo'] = soup_curso.find('tr').findAll('td')[1].text.replace(' ', '').replace('\n', '').strip()
                curso['nombre'] = soup_curso.findAll('tr')[2].findAll('td')[1].text.replace('\n', '').strip()
                curso['creditos'] = int(soup_curso.findAll('tr')[2].findAll('td')[3].text.replace(' ', '').replace('\n', '').strip())
                curso['estado'] = 'CERRADO'
                curso['notas'] = []
                soup_notas = soup_curso.findAll('tr')[5:-1]
                # Iterar por cada nota
                for soup_nota in soup_notas:
                    # Construir nota
                    nota = {}
                    nota['tipo'] = soup_nota.findAll('td')[0].text.replace(' ', '').replace('\n', '').strip()
                    nota['evaluacion'] = soup_nota.findAll('td')[1].text.replace('\n', '').strip()
                    nota['numero'] = int(soup_nota.findAll('td')[2].text.replace(' ', '').replace('\n', '').strip())
                    peso_str = soup_nota.findAll('td')[3].text.replace(' ', '').replace('\n', '').strip().replace('%', '')
                    nota['peso'] = float(peso_str if peso_str.replace('.', '').isnumeric() else 0.0) / 100
                    nota_str = soup_nota.findAll('td')[4].text.replace(' ', '').replace('\n', '').strip()
                    nota['nota'] = float(nota_str if nota_str.replace('.', '').isnumeric() else 0.0)
                    nota['obs'] = (nota_str if not nota_str.replace('.', '').isnumeric() else None) if nota_str != '' else 'P'
                    if nota['obs'] == 'RET':
                        curso['estado'] = 'RETIRADO'
                    if nota['obs'] == 'P':
                        curso['estado'] = 'CURSANDO'
                    curso['notas'].append(nota)
                if curso['estado'] == 'CERRADO' and ciclo['estado'] != 'CURSANDO':
                    ciclo['estado'] = 'CERRADO'
                if curso['estado'] == 'CURSANDO':
                    ciclo['estado'] = 'CURSANDO'
                ciclo['cursos'].append(curso)
            consolidado['ciclos'].append(ciclo)
    # endregion
    return consolidado
