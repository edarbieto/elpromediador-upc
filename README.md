# El Promediador - UPC

Una aplicacion para la visualizacion de notas y promediar las mismas de manera interactiva y rapida. La logica detras del scraping, promedio y calculo de notas es independiente de la interfaz (responsive web por el momento), permitiendo de esta forma migrar a aplicacion movil, escritorio, etc.

## Modulos

- Scraping web intranet upc (cloudflare bypassing incluido).
- Promedio de notas actuales interactiva.
- Calculo de notas aun por rendir para alcanzar una meta (beca, nota promedio especifica, subir o bajar X puntos del promedio acumulado en el ciclo).

## Tecnologias

- Python 3
- Vue JS
- Google Cloud

## Librerias

| Logica | Backend | Frontend |
| - | - | - |
| cfsrape (custom)<br>requests<br>bs4 | flask | vuejs |

## Despliegue

La aplicacion se desplegara en una instancia free de Google Cloud con su propio nombre de dominio. 

## TODO:

- Backend (API)
- Frontend (responsive)
- Despliegue

Este proyecto esta dirigido a todo alumno de la UPC con un codigo y contrasena vigente. No se recolecta ninguna informacion de los usuarios ni se ofrece a terceros. Este es un proyecto libre y cualquiera puede solicitar una demostracion de lo que afirmo.

Cualquier contacto y sugerencia me pueden escribir a edarbieto@gmail.com