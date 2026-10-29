# PLN · TP1, TP2 y TP3 · Grupo 7

Procesamiento del Lenguaje Natural, Tecnicatura Universitaria en Inteligencia Artificial (FCEIA, UNR). Comisión 2.

## Integrantes

| Integrante | Legajo |
|---|---|
| Civetta, Valentino | 45948755 |
| Frank, Maximiliano | 38726401 |
| Fucci, Milagros | 47076861 |
| Winter, Federico | 44101265 |

Docentes: Geary, Alan y Manson, Juan Pablo.

## De qué se trata

En el **TP1** armamos un corpus propio: 150 libros de la categoría "Clásico" de [Lectulandia](https://ww3.lectulandia.co/genero/clasico/), con sus metadatos y sinopsis, extraídos con Playwright y BeautifulSoup.

En el **TP2** convertimos esas sinopsis en vectores con tres modelos (un Word2Vec entrenado por nosotros, el Word2Vec pre-entrenado SBW y el modelo de oración SBERT), los guardamos en Supabase con pgvector, armamos un buscador semántico en SQL y lo evaluamos contra TF-IDF y contra el azar con 12 consultas propias. Como parte avanzada hicimos un RAG con la API de NVIDIA NIM.

En el **TP3** armamos un recomendador personalizado de libros. Partimos de un catálogo de 8747 libros que la cátedra contaminó a propósito: enlaces, mensajes promocionales y libros inventados. Primero lo auditamos con varios detectores (expresiones regulares, normalización de Unicode, detección de idioma, NER, clasificadores de oraciones con TF-IDF y con embeddings, y vecinos más cercanos para encontrar copias). Después, con las preferencias de una persona del grupo, entrenamos clasificadores que ordenan los libros que todavía no leyó. Todo lo del TP3 está en la carpeta `tp3/`, como pide la consigna.

## Estructura del repositorio

```
README.md                 este archivo
requirements.txt          dependencias de Python
.env.example              plantilla de credenciales (el .env real no se sube)
.gitignore
queries.json              TP2: conjunto de evaluación (12 consultas con sus libros relevantes)
informe_tp2.pdf           TP2: informe (carátula + 3 páginas)
data/
  libros.csv              TP1: corpus de 150 libros
src/
  scraper.py              TP1: scraper de Lectulandia
  TP2_Civetta_Frank_Fucci_Winter.ipynb   TP2: notebook ejecutado, con salidas
docs/
  TP-1.pdf, TP-2.pdf      consignas de la cátedra
  diseno_extraccion.md    TP1: diseño de la extracción (Parte 1 de la consigna)
  informe_fuente.md       TP2: fuente del informe (pandoc + xelatex)
  logo_fceia.png          logo usado en la carátula del informe
tp3/                      TP3: todo lo de la entrega
  TP3_Civetta_Frank_Fucci_Winter.ipynb   notebook ejecutado (pasos 1 a 8 y conclusiones)
  grupo7_sospechosos.csv  libros marcados en la auditoría (slug y motivo)
  grupo7_preferencias.csv valoraciones del lector, con la columna conjunto
  informe_tp3.pdf         informe (carátula + 2 páginas)
  data/
    catalogo_tp3.jsonl    catálogo de la cátedra, 8747 libros (algunos contaminados)
    muestra_etiquetada.csv   500 libros con la columna contaminado (también en .xlsx)
    catalogo_limpio.csv   catálogo sin los sospechosos (lo genera el paso 2.7)
    ejemplo_sospechosos.csv, ejemplo_preferencias.csv   formato de los archivos de entrega (también en .xlsx)
  docs/
    TP-3.pdf              consigna de la cátedra
    informe_tp3_fuente.md fuente del informe (pandoc + xelatex)
    logo_fceia.png        logo de la carátula
```

Hay archivos que existen en cada máquina pero no se suben (están en `.gitignore`): `.env`, el modelo SBW (`data/SBW-vectors-300-min5.bin.gz`, 1,1 GB, el notebook lo descarga solo si falta), el entorno virtual y la guía de estudio interna `docs/guia_estudio_tp2.pdf`.

## Instalación

```bash
git clone <URL_DEL_REPO>
cd <carpeta_del_repo>
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium      # solo hace falta para correr el scraper del TP1
python -m spacy download es_core_news_lg   # solo hace falta para el TP3 (NER y frases sustantivas)
```

## Credenciales: `.env` y `.env.example`

El notebook necesita dos datos secretos: la URL de conexión a la base de Supabase (con su contraseña) y una clave de la API de NVIDIA NIM. Esos datos van en un archivo `.env` en la raíz del repo, que git ignora, así que nunca terminan en GitHub.

`.env.example` es la plantilla que sí se sube. Muestra qué variables hacen falta, con valores de ejemplo, para que cualquiera pueda armar su `.env`:

1. Copiar la plantilla: `cp .env.example .env` (en Windows: `copy .env.example .env`).
2. En `SUPABASE_DB_URL`, reemplazar `<PEDIR_AL_GRUPO>` por la contraseña, que se comparte por privado dentro del grupo.
3. En `NVIDIA_API_KEY`, poner una clave personal de [build.nvidia.com](https://build.nvidia.com). Solo hace falta para la parte avanzada (RAG).

El notebook del TP2 lee esas variables con `load_dotenv()`. El TP3 no usa credenciales.

**En Google Colab** no hay `.env`. Cargar `SUPABASE_DB_URL` y `NVIDIA_API_KEY` en los *Secrets* de Colab (el ícono de la llave) y ejecutar esto antes de la Parte E:

```python
import os
from google.colab import userdata
for nombre in ["SUPABASE_DB_URL", "NVIDIA_API_KEY"]:
    os.environ[nombre] = userdata.get(nombre)
```

`load_dotenv()` no pisa una variable que ya está definida, así que el notebook funciona igual en los dos casos.

## Cómo correr cada TP

**TP1 (scraper):** `python src/scraper.py`. Corre sin abrir ventana, espera 2 segundos entre fichas, guarda cada libro apenas lo procesa y reescribe `data/libros.csv` en cada ejecución. La categoría, la URL y la cantidad de libros se cambian en las constantes del principio del archivo (`CATEGORIA`, `URL_CATEGORIA`, `LIBROS_OBJETIVO`).

**TP2 (notebook):** abrir `src/TP2_Civetta_Frank_Fucci_Winter.ipynb` y ejecutar todas las celdas en orden, con el `.env` armado. La primera vez descarga SBW (1,1 GB) y el modelo SBERT, así que tarda bastante; después la corrida completa lleva unos 10 minutos. Las rutas son relativas a `src/`, así que el notebook se tiene que abrir desde esa carpeta.

**TP3 (notebook):** abrir `tp3/TP3_Civetta_Frank_Fucci_Winter.ipynb` desde la carpeta `tp3/` y correr las celdas en orden. Lee los datos de `tp3/data/` y guarda los dos CSV de entrega en `tp3/`. El paso 3 lo corre solo el lector: muestra un libro por vez, guarda cada respuesta en el momento y se puede cortar y retomar. Como `grupo7_preferencias.csv` ya está completo, si se vuelve a correr no pregunta nada. Nosotros lo ejecutamos en Google Colab con GPU; ahí hay que descomentar la celda de instalación y poner `RUTA` y `ENTREGA` en `/content/` (o la carpeta donde se suban los archivos). El paso 2.7 codifica decenas de miles de oraciones con SBERT: con GPU tarda unos minutos y con CPU bastante más.

## Resultados del TP3

En el paso 1 quedaron 8593 libros del catálogo original.

| Motivo | Libros eliminados |
|---|---|
| Sin sinopsis | 1 |
| Sinopsis repetida (cursos y series completas) | 98 |
| Casi duplicado (mismo autor, título parecido, mismo tomo, sinopsis casi igual) | 55 |

En la auditoría (paso 2) medimos cada detector sobre la parte de prueba de la muestra etiquetada (150 libros, 30 contaminados):

| Detector | Precisión | Recall |
|---|---|---|
| Expresión regular | 1,00 | 0,23 |
| Normalización + dominios | 1,00 | 0,63 |
| Idioma por oración | 0,62 | 0,33 |
| Clasificador de oraciones TF-IDF | 1,00 | 0,93 |
| Clasificador de oraciones con embeddings | 0,90 | 0,87 |
| Copias (vecino más cercano) | 1,00 | 0,10 |
| Combinación (al menos uno) | 0,79 | 1,00 |

En el catálogo completo marcamos 703 libros (8,2 %) y quedaron 7890 en `catalogo_limpio.csv`. El detector de idioma es el que más falsos positivos suma.

El lector fue Valentino Civetta: valoró 101 libros (46 le interesaron, 54 no y uno quedó sin decidir). Con 80 libros para entrenar y 20 para probar:

| Lista de recomendación | F1 clase 1 (prueba) | F1 validación cruzada | precision@5 |
|---|---|---|---|
| TF-IDF + regresión logística | 0,35 | 0,42 ± 0,19 | 0,20 |
| Embeddings + regresión logística | 0,52 | 0,53 ± 0,16 | 0,80 |
| Similitud con el perfil del lector | | | 0,20 |
| Azar | | | 0,45 |

El clasificador con embeddings fue el único que recomendó mejor que el azar, aunque con 20 libros de prueba parte de esa diferencia puede ser suerte. En el catálogo completo recomendó cinco libros de intriga, espionaje y Segunda Guerra, y al lector le interesaron dos. El análisis completo está en el notebook y en `tp3/informe_tp3.pdf`.

## Resultados del TP2

| Método | P@5 | P@10 | R-precision |
|---|---|---|---|
| Azar (esperado) | 0,025 | 0,025 | 0,025 |
| TF-IDF | 0,283 | 0,217 | 0,357 |
| Word2Vec propio | 0,167 | 0,125 | 0,159 |
| SBW | 0,267 | 0,208 | 0,286 |
| SBERT | 0,350 | 0,258 | 0,466 |

SBERT es el mejor en promedio y en los tres tipos de consulta, aunque con 12 consultas la diferencia con TF-IDF no es estadísticamente concluyente. El análisis completo, el caso de falla y el RAG están en `informe_tp2.pdf` y en el notebook.

## TP1: dificultades que encontramos

- **La sinopsis no tiene siempre la misma estructura.** En algunas fichas el texto está dentro de un `<p class="description">` y en otras va directo en el `<div id="sinopsis">`. Lo resolvimos con el selector `#sinopsis`, que cubre los dos casos (ver `docs/diseno_extraccion.md`, sección 3).
- **El número de libro dentro de una serie no tiene etiqueta propia.** Aparece mezclado con el nombre de la serie ("Libro 9 de: ..."), así que lo sacamos con una expresión regular sobre el `<span class="tagTitle">`.
- **Las corridas se acumulaban.** La primera versión agregaba los libros al final del CSV existente, y cada ejecución sumaba datos de la anterior. Ahora el script borra el CSV al empezar.

## TP1: campos de `data/libros.csv`

| Campo | Descripción | Tipo |
|---|---|---|
| titulo | Título del libro | texto |
| autores | Lista de autores | texto |
| generos | Lista de géneros | texto |
| serie | Serie a la que pertenece, o "N/A" | texto |
| numero_serie | Número dentro de la serie, o "N/A" | texto |
| sinopsis | Sinopsis completa | texto |
| url_libro | URL de la ficha (identifica a cada libro) | texto |
| categoria_origen | Categoría del scraping | texto |
| fecha_extraccion | Fecha y hora de extracción | fecha y hora |
