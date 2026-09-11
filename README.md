# TP1 NLP — Extracción y procesamiento de texto (TUIA)

**Comisión:** 2 (TUIA) — Grupo: Civetta/Fucci

## Integrantes
- Civetta Valentino — Legajo: 45948755
- Fucci Milagros — Legajo: 47076861
- Winter Federico — Legajo: 44101265
- Frank Maximiliano — Legajo: 38726401

**Docentes:** GEARY, Alan — MANSON, Juan Pablo

## Categoría seleccionada
**Clásico** — https://ww3.lectulandia.co/genero/clasico/

## Cantidad de libros extraídos
_Pendiente: completar con la cantidad real obtenida al finalizar la ejecución del script._

El objetivo configurado en `scraper.py` (constante `LIBROS_OBJETIVO`) es de **150 libros**. El script se detiene automáticamente al alcanzar esa cantidad, o antes si la categoría se queda sin páginas de listado disponibles.

## Instrucciones de instalación

```bash
git clone <URL_DEL_REPO>
cd PLN_Grupo7_Civetta_Fucci_Frank_Winter
python -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

`requirements.txt` debe incluir:

```
playwright
beautifulsoup4
pandas
```

(Las librerías `asyncio`, `os`, `re` y `datetime` que también usa `scraper.py` son parte de la biblioteca estándar de Python, no requieren instalación aparte.)

## Instrucciones para ejecutar el programa

```bash
python src/scraper.py
```

El script:
- Corre en modo **headless** (sin abrir ventana del navegador) por configuración fija en el código.
- **Sobrescribe** el archivo `data/libros.csv` en cada ejecución (si existe uno de una corrida anterior, lo elimina antes de empezar), para que el CSV final siempre corresponda a la corrida más reciente.
- Guarda los resultados de forma **incremental**, fila por fila, a medida que se procesa cada libro — si el proceso se interrumpe a mitad de camino, los libros ya extraídos hasta ese punto no se pierden.
- Aplica una pausa de 2 segundos entre cada ficha visitada, para no sobrecargar el servidor del sitio.
- No requiere parámetros por línea de comandos: la categoría, la URL base y la cantidad objetivo de libros se configuran editando las constantes al inicio de `scraper.py` (`CATEGORIA`, `URL_CATEGORIA`, `LIBROS_OBJETIVO`).

## Principales dificultades encontradas

- **Inconsistencia estructural entre fichas del sitio:** se detectó que la sección de sinopsis no tiene siempre la misma estructura interna — en algunas fichas el texto está envuelto en un `<p class="description">`, y en otras queda como texto plano directo dentro del `<div id="sinopsis">`. Se resolvió usando un selector más genérico (`#sinopsis`) que cubre ambos casos sin necesidad de lógica condicional adicional (ver detalle en `docs/diseno_extraccion.md`, sección 3).
- **Extracción del número de libro dentro de una serie:** el número (ej. "Libro 9 de: ...") no está aislado en una etiqueta propia, sino mezclado como texto junto con el nombre de la serie. Se resolvió con una expresión regular sobre el texto del `<span class="tagTitle">` correspondiente.
- **Guardado incremental vs. acumulación entre corridas:** la primera versión del script agregaba (`append`) los libros nuevos al final del CSV existente, lo que hacía que ejecuciones sucesivas fueran acumulando datos de corridas anteriores en vez de generar un dataset limpio. Se corrigió agregando un paso inicial que elimina el CSV previo antes de empezar cada corrida.
- **Organización del repositorio:** la cátedra solicita un repositorio independiente por materia; el material se encontraba inicialmente como un subdirectorio dentro de un repositorio maestro más amplio (TUIA). Se resolvió migrando el historial del subdirectorio a un repositorio propio y enlazándolo al repositorio maestro como submódulo de Git.

## Estructura del repositorio

```
README.md
src/
  scraper.py
data/
  libros.csv
docs/
  diseno_extraccion.md
```
