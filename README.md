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
_Pendiente: completar una vez finalizada la Parte 2 (implementación). El objetivo es extraer entre 50 y 100 libros de la categoría Clásico._

## Instrucciones de instalación

```bash
git clone <URL_DEL_REPO>
cd PLN_Grupo7_Civetta_Fucci_Frank_Winter
python -m venv venv
source venv/bin/activate   # en Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

_Nota: falta agregar el archivo `requirements.txt` (playwright, beautifulsoup4, pandas) una vez armado el `scraper.py`._

## Instrucciones para ejecutar el programa

```bash
python src/scraper.py
```

_Pendiente: detallar parámetros de ejecución (por ejemplo, modo headless, cantidad de páginas a recorrer) una vez implementado el script._

## Principales dificultades encontradas
_Pendiente: completar durante/después de la implementación (Parte 2)._

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
